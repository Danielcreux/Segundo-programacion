import os
import re
import json
import requests
import mysql.connector
from functools import lru_cache
from flask import Flask, request, render_template_string, session, redirect, url_for, flash, jsonify

# ===================== CONFIG =====================
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "crimson"),
    "password": os.environ.get("MYSQL_PASSWORD", "crimson"),
    "database": os.environ.get("MYSQL_DATABASE", "crimson"),
    "connection_timeout": 5,
}

OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

SCHEMA_PATH = os.environ.get("SCHEMA_PATH", "aplicacion.sql")
MAX_SCHEMA_CHARS = 80_000
DEFAULT_LIMIT = int(os.environ.get("DEFAULT_LIMIT", "200"))
MAX_EXEC_MS = int(os.environ.get("MAX_EXEC_MS", "1500"))  # 1.5 s
MAX_ANALYSIS_ROWS = int(os.environ.get("MAX_ANALYSIS_ROWS", "50"))
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
CLEAR_ON_NEW_QUERY = True
ALLOW_DML = os.environ.get("ALLOW_DML", "true").lower() in ("1", "true", "yes", "y")

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------- Compactador de esquema ----------
CREATE_TBL_RE = re.compile(
    r"CREATE\s+TABLE\s+`?([A-Za-z0-9_]+)`?\s*\((.*?)\)\s*ENGINE=",
    re.IGNORECASE | re.DOTALL
)
CREATE_VIEW_RE = re.compile(
    r"CREATE\s+.*?\sVIEW\s+`?([A-Za-z0-9_]+)`?\s+AS\s+(.*?);",
    re.IGNORECASE | re.DOTALL
)

def _clean_cols(block: str) -> list:
    cols = []
    for line in block.splitlines():
        line = line.strip().rstrip(",")
        if not line or line.upper().startswith(("PRIMARY KEY", "KEY ", "UNIQUE KEY", "CONSTRAINT", "FOREIGN KEY")):
            continue
        m = re.match(r"`?([A-Za-z0-9_]+)`?\s+([A-Za-z0-9\(\),._\s]+)", line)
        if m:
            cols.append((m.group(1), m.group(2).split()[0]))
    return cols

def compact_schema(sql_text: str) -> str:
    out = []
    for m in CREATE_TBL_RE.finditer(sql_text):
        tname = m.group(1)
        cols = _clean_cols(m.group(2))
        cols_txt = ", ".join([f"`{c}` {t}" for c, t in cols[:64]])
        out.append(f"TABLE `{tname}` ( {cols_txt} )")
    for m in CREATE_VIEW_RE.finditer(sql_text):
        vname = m.group(1)
        sel = " ".join(m.group(2).split())
        if len(sel) > 800: sel = sel[:800] + " …"
        out.append(f"VIEW `{vname}` AS {sel}")
    txt = "\n".join(out)
    if len(txt) > MAX_SCHEMA_CHARS:
        txt = txt[:MAX_SCHEMA_CHARS] + "\n-- [Truncado]\n"
    return txt

@lru_cache(maxsize=1)
def cargar_schema_compacto(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    return compact_schema(raw)

# ---------- Prompts & LLM ----------
def build_prompt(schema_sql: str, user_question: str) -> str:
    """
    Permitimos SELECT e instrucciones DML (INSERT/UPDATE/DELETE) si el usuario las pide.
    Mantenemos respuesta con UN único bloque SQL y ENDSQL.
    """
    examples = (
        "### Formato estricto\n"
        "Responde SOLO con:\n"
        "1) 1-2 frases de explicación\n"
        "2) Un ÚNICO bloque de SQL dentro de ```sql```\n"
        "Tras el bloque, escribe ENDSQL en una nueva línea.\n\n"
        "### Ejemplos\n"
        "Explicación: Últimos 10 clientes por Identificador.\n"
        "```sql\n"
        "SELECT * FROM clientes ORDER BY Identificador DESC LIMIT 10\n"
        "```\n"
        "ENDSQL\n\n"
        "Explicación: Actualiza el estado de un pedido.\n"
        "```sql\n"
        "UPDATE pedidos SET estado = 'enviado' WHERE id = 123\n"
        "```\n"
        "ENDSQL\n"
    )
    contexto = (
        "Eres un asistente SQL conciso. Usa EXCLUSIVAMENTE el esquema siguiente.\n"
        "Evita DDL. Si el usuario pide insertar/actualizar/borrar, genera una única sentencia DML.\n"
        "Para SELECT: usa LIMIT y filtros simples.\n\n"
        "=== ESQUEMA (compacto) ===\n"
        f"{schema_sql}\n"
        "=== FIN ESQUEMA ===\n\n"
        f"{examples}"
        f"Pregunta del usuario:\n{user_question}\n"
    )
    return contexto

def build_results_comment_prompt(question: str, sql: str, sql_type: str, cols: list, rows: list, rowcount: int, limit_rows: int) -> str:
    # previsualización para SELECT
    preview = []
    if rows and cols and sql_type == "select":
        for r in rows[:limit_rows]:
            preview.append([("" if v is None else (v.decode() if isinstance(v, (bytes, bytearray)) else str(v))) for v in r])

    payload = {
        "question": question,
        "sql": sql,
        "sql_type": sql_type,
        "columns": cols if cols else [],
        "preview_rows": preview,
        "row_count_shown": min(len(rows) if rows else 0, limit_rows),
        "row_count_total": len(rows) if rows else 0,
        "affected": rowcount if rowcount is not None else 0
    }

    if sql_type == "select":
        task = ("Redacta 2–5 viñetas con observaciones claras y útiles sobre los resultados "
                "(tendencias, valores extremos, conteos, advertencias de calidad). Máx. 80 palabras.")
    else:
        task = ("Redacta 2–4 viñetas resumiendo la operación DML (qué hace, alcance, filas afectadas, "
                "riesgos o comprobaciones sugeridas). Máx. 60 palabras. No inventes datos.")

    return (
        "Actúa como analista de datos.\n"
        f"{task}\n\n"
        "### Contexto\n"
        f"Pregunta del usuario: {question}\n"
        f"SQL ejecutado:\n{sql}\n\n"
        "### Datos (JSON)\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
    )

def ollama_healthcheck(base: str) -> None:
    try:
        r = requests.get(f"{base}/api/version", timeout=3)
        if r.status_code != 200:
            raise RuntimeError(f"Ollama respondió {r.status_code} en /api/version.")
    except Exception as e:
        raise RuntimeError(
            f"No se puede conectar a Ollama en {base}. "
            f"¿Ejecutaste `ollama serve`? Detalle: {e}"
        )

def call_ollama(prompt: str, *, temperature: float = 0.2, stop=None, num_predict: int = 220) -> str:
    ollama_healthcheck(OLLAMA_BASE)
    options = {
        "temperature": temperature,
        "top_p": 0.9,
        "num_ctx": 2048,
        "num_predict": num_predict,
    }
    if stop:
        options["stop"] = stop
    r = requests.post(
        f"{OLLAMA_BASE}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False, "options": options},
        timeout=300,
    )
    if r.status_code != 200:
        try:
            payload = r.json()
        except Exception:
            payload = {"error": r.text}
        raise RuntimeError(
            f"Ollama chat error {r.status_code} — {payload.get('error') or payload} "
            f"(base={OLLAMA_BASE} model={OLLAMA_MODEL})"
        )
    obj = r.json()
    return (obj.get("message", {}).get("content") or obj.get("response") or "").strip()

SQL_BLOCK_RE = re.compile(r"```sql\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)

def extract_sql_from_llm(text: str) -> str:
    m = SQL_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip().rstrip(";")
    for ln in text.splitlines():
        if ln.lower().startswith("select ") or ln.lower().startswith(("insert ", "update ", "delete ")):
            return ln.strip().rstrip(";")
    return ""

def ensure_limit(sql: str, default_limit: int = DEFAULT_LIMIT) -> str:
    low = sql.lower()
    if not low.strip().startswith("select"):
        return sql
    if " limit " in low:
        return sql
    if " count(" in low and " group by " not in low:
        return sql
    return f"{sql} LIMIT {default_limit}"

def add_max_exec_hint(sql: str, ms: int = MAX_EXEC_MS) -> str:
    if not sql.lower().strip().startswith("select"):
        return sql
    return re.sub(r"(?is)\A(\s*select\s+)", rf"\1/*+ MAX_EXECUTION_TIME({ms}) */ ", sql, count=1)

def classify_sql_type(sql: str) -> str:
    s = sql.strip().lower()
    if s.startswith("select"):
        return "select"
    if s.startswith("insert"):
        return "insert"
    if s.startswith("update"):
        return "update"
    if s.startswith("delete"):
        return "delete"
    return "other"

def is_safe_query(sql: str) -> (bool, str):
    """
    Permitimos SELECT siempre.
    Permitimos INSERT/UPDATE/DELETE solo si ALLOW_DML==True.
    Bloqueamos DDL y características peligrosas.
    Bloqueamos multi-sentencias usando ';' fuera de strings (heurística simple).
    """
    lowered = f" {sql.lower()} "
    forbidden = [" drop ", " alter ", " truncate ", " grant ", " revoke ", " outfile ", " infile "]
    if any(tok in lowered for tok in forbidden) or ";" in lowered.strip()[1:-1]:
        return False, "Operación no permitida por seguridad (DDL, OUTFILE/INFILE o multi-sentencia)."

    typ = classify_sql_type(sql)
    if typ == "select":
        return True, ""
    if typ in ("insert", "update", "delete"):
        if not ALLOW_DML:
            return False, "DML deshabilitado. Habilítalo con ALLOW_DML=true."
        return True, ""
    return False, "Solo se permiten SELECT o DML básicos (INSERT/UPDATE/DELETE)."

def run_query(sql: str):
    """
    Ejecuta SELECT o DML.
    Devuelve: (sql_type, cols, rows, rowcount)
    - SELECT: cols/lista de filas, rowcount=len(rows)
    - DML: cols=None, rows=None, rowcount=cursor.rowcount
    """
    typ = classify_sql_type(sql)
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cur = conn.cursor()
        if typ == "select":
            cur.execute(f"SET SESSION max_execution_time={MAX_EXEC_MS}")
            cur.execute(add_max_exec_hint(ensure_limit(sql)))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            return typ, cols, rows, len(rows)
        else:
            cur.execute(sql)
            conn.commit()
            return typ, None, None, cur.rowcount
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

# ---------- UI (Tema claro, profesional) ----------
PAGE = """
<!doctype html>
<html lang="es" class="notranslate" translate="no">
<head>
  <meta charset="utf-8" />
  <title>AI SQL Chat · ligero</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root{
      --bg: #f7f8fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #5b6472;
      --primary: #1f6feb; /* azul suave GitHub-like */
      --primary-ink: #0f3f9c;
      --border: #e6e8f0;
      --accent: #2ea043; /* verde suave */
      --warn: #b54708;
      --err: #b42318;
      --shadow: 0 6px 20px rgba(16,24,40,.08);
      --radius: 14px;
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0; background: var(--bg); color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
      -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
    }
    .wrap{ max-width: 1100px; margin: 0 auto; padding: 24px 24px 120px; } /* espacio inferior para input sticky */
    header{
      background: var(--card); border:1px solid var(--border); border-radius: var(--radius); padding: 16px 18px;
      box-shadow: var(--shadow);
    }
    header h1{ margin:0 0 6px; font-size:20px; letter-spacing:.2px }
    header .sub{ color: var(--muted); font-size:14px }
    .pillbar{ display:flex; gap:8px; flex-wrap:wrap; margin-top:8px }
    .pill{ padding:6px 10px; font-size:12px; border:1px solid var(--border); border-radius:999px; background:#fafbff }
    .pane{
      margin-top:16px; background:var(--card); border:1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); padding:14px;
    }
    .title{ font-weight:600; }
    .insights{ background:#f8fafc; border:1px solid var(--border); padding:12px; border-radius: 10px; }
    .insights h3{ margin:0 0 8px; font-size:14px; color:#0f3f9c }
    .flash{ background:#fff7ed; border:1px solid #fed7aa; color:#9a3412; padding:10px 12px; border-radius:10px; margin:8px 0; }
    .error{ background:#fef2f2; border-color:#fecaca; color:#b91c1c }
    .meta{ color: var(--muted); font-size:12px; margin-top:6px }
    /* Tabla clara y legible */
    table{ width:100%; border-collapse: collapse; font-size:14px; margin-top:10px }
    thead th{ position: sticky; top: 0; background:#f3f4f6; }
    th, td{ border:1px solid var(--border); padding:8px 10px; text-align:left }
    tbody tr:nth-child(odd){ background:#fcfcfe }
    tbody tr:hover{ background:#f5f7ff }
    /* Input fijo abajo */
    .dock{
      position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255,255,255,.85); backdrop-filter: blur(6px);
      border-top:1px solid var(--border); box-shadow: 0 -6px 20px rgba(16,24,40,.06);
    }
    .dock-inner{ max-width:1100px; margin:0 auto; padding:12px 24px; display:flex; gap:10px }
    input[type=text]{
      flex:1; padding:12px 14px; background:#ffffff; border:1px solid var(--border); border-radius:10px; outline:none;
    }
    input[type=text]::placeholder{ color:#98a2b3 }
    button{
      padding:12px 14px; border-radius:10px; border:1px solid #1f6feb26; color:#fff; background:linear-gradient(180deg, var(--primary), #1a61d0);
      cursor:pointer; font-weight:600;
      transition:.08s transform ease, .2s filter ease;
    }
    button:hover{ filter: brightness(1.02) }
    button:active{ transform: translateY(1px) }
    a{ color: var(--primary) }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>AI SQL Chat</h1>
      <div class="sub">Resultados arriba, consulta abajo. Tema claro y profesional.</div>
      <div class="pillbar">
        <div class="pill">BD: <b>{{ db }}</b></div>
        <div class="pill">Modelo: <code>{{ model }}</code></div>
        <div class="pill">Límite SELECT: {{ dlimit }}</div>
        <div class="pill">Max. {{ ms }} ms</div>
        <div class="pill">Esquema: {{ schema_path }}</div>
        <div class="pill"><a href="{{ url_for('health') }}">/health</a></div>
      </div>
    </header>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for m in messages %}
          <div class="pane flash">{{ m }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if history %}
      {% for turn in history %}
        <div class="pane">
          <div class="title">{{ turn.title }}</div>
          <div class="meta" style="margin-bottom:10px">{{ turn.subtitle }}</div>

          {% if turn.commentary %}
            <div class="insights">
              <h3>Comentario</h3>
              {{ turn.commentary|safe }}
            </div>
          {% endif %}

          {% if turn.show_table %}
            <div style="max-height: 540px; overflow:auto; border-radius:10px; margin-top:10px">
              <table>
                <thead>
                  <tr>
                    {% for c in turn.cols %}<th>{{ c }}</th>{% endfor %}
                  </tr>
                </thead>
                <tbody>
                  {% for r in turn.rows %}
                    <tr>
                      {% for cell in r %}
                        <td>{{ cell }}</td>
                      {% endfor %}
                    </tr>
                  {% endfor %}
                  {% if not turn.rows %}
                    <tr><td colspan="{{ turn.cols|length }}">(Sin filas)</td></tr>
                  {% endif %}
                </tbody>
              </table>
            </div>
          {% endif %}

          {% if turn.error %}
            <div class="flash error" style="margin-top:10px">{{ turn.error }}</div>
          {% endif %}
        </div>
      {% endfor %}
    {% endif %}
  </div>

  <!-- Dock inferior con el formulario -->
  <div class="dock">
    <form class="dock-inner" method="post" action="{{ url_for('chat') }}">
      <input type="text" name="q" placeholder="Escribe tu consulta o acción: SELECT, INSERT, UPDATE o DELETE…" required>
      <button type="submit">Ejecutar</button>
    </form>
  </div>
</body>
</html>
"""

# ---------- Rutas ----------
@app.route("/", methods=["GET"])
def index():
    session.setdefault("history", [])
    return render_template_string(
        PAGE,
        history=session["history"],
        model=OLLAMA_MODEL,
        dlimit=DEFAULT_LIMIT,
        ms=MAX_EXEC_MS,
        db=MYSQL_CONFIG["database"],
        schema_path=SCHEMA_PATH,
    )

@app.route("/", methods=["POST"])
def chat():
    q = request.form.get("q", "").strip()
    if not q:
        flash("Escribe una pregunta o instrucción SQL.")
        return redirect(url_for("index"))

    # Mostrar solo la consulta actual
    if CLEAR_ON_NEW_QUERY:
        session["history"] = []
    else:
        session.setdefault("history", [])

    schema = cargar_schema_compacto(SCHEMA_PATH)

    # 1ª llamada: generar SQL (SELECT o DML, según la petición)
    try:
        llm_text = call_ollama(build_prompt(schema, q), stop=["ENDSQL"])
    except Exception as e:
        session["history"].append({
            "title": "Error al generar SQL",
            "subtitle": q,
            "commentary": None,
            "show_table": False,
            "cols": None,
            "rows": None,
            "error": f"LLM falló: {e}",
        })
        session.modified = True
        return redirect(url_for("index"))

    sql = extract_sql_from_llm(llm_text)
    if not sql:
        session["history"].append({
            "title": "No se pudo extraer SQL",
            "subtitle": q,
            "commentary": None,
            "show_table": False,
            "cols": None,
            "rows": None,
            "error": "La respuesta no contenía un bloque SQL válido.",
        })
        session.modified = True
        return redirect(url_for("index"))

    ok, why = is_safe_query(sql)
    if not ok:
        session["history"].append({
            "title": "Consulta bloqueada por seguridad",
            "subtitle": sql,
            "commentary": None,
            "show_table": False,
            "cols": None,
            "rows": None,
            "error": why,
        })
        session.modified = True
        return redirect(url_for("index"))

    # Ejecutar
    try:
        typ, cols, rows, rowcount = run_query(sql)
        # SQL final con hints si SELECT
        final_sql = add_max_exec_hint(ensure_limit(sql)) if typ == "select" else sql

        # 2ª llamada: comentario AI (siempre)
        try:
            comment_prompt = build_results_comment_prompt(q, final_sql, typ, cols, rows, rowcount, MAX_ANALYSIS_ROWS)
            comment_text = call_ollama(comment_prompt, temperature=0.2, num_predict=220)
            # Normalizar a viñetas HTML
            if any(b in comment_text for b in ("- ", "•")):
                formatted = "<ul>" + "".join(
                    f"<li>{line.strip('•- ').strip()}</li>"
                    for line in comment_text.splitlines() if line.strip()
                ) + "</ul>"
            else:
                bullets = [s.strip() for s in re.split(r"[•\-]\s+|(?<=\.)\s+", comment_text) if s.strip()]
                formatted = "<ul>" + "".join(f"<li>{b}</li>" for b in bullets[:5]) + "</ul>"
        except Exception as e2:
            formatted = f"<div class='flash'>No se pudo generar comentario: {e2}</div>"

        # Componer tarjeta de resultado (sin mostrar la SQL como pediste)
        if typ == "select":
            title = "Resultados de la consulta"
            subtitle = f"{len(rows)} fila{'s' if len(rows)!=1 else ''} · SELECT con límite y tiempo máximo aplicados"
            show_table = True
        elif typ == "insert":
            title = "Inserción realizada"
            subtitle = f"{rowcount} fila{'s' if rowcount!=1 else ''} insertada(s)"
            show_table = False
        elif typ == "update":
            title = "Actualización realizada"
            subtitle = f"{rowcount} fila{'s' if rowcount!=1 else ''} actualizada(s)"
            show_table = False
        elif typ == "delete":
            title = "Borrado realizado"
            subtitle = f"{rowcount} fila{'s' if rowcount!=1 else ''} borrada(s)"
            show_table = False
        else:
            title = "Operación completada"
            subtitle = q
            show_table = bool(cols)

        session["history"].append({
            "title": title,
            "subtitle": subtitle,
            "commentary": formatted,
            "show_table": show_table,
            "cols": cols if show_table else None,
            "rows": rows if show_table else None,
            "error": None,
        })

    except Exception as e:
        session["history"].append({
            "title": "Error al ejecutar SQL",
            "subtitle": sql,
            "commentary": None,
            "show_table": False,
            "cols": None,
            "rows": None,
            "error": f"{e}",
        })

    session.modified = True
    return redirect(url_for("index"))

@app.route("/health")
def health():
    info = {"ollama_base": OLLAMA_BASE, "model": OLLAMA_MODEL, "schema_path": SCHEMA_PATH, "allow_dml": ALLOW_DML}
    try:
        v = requests.get(f"{OLLAMA_BASE}/api/version", timeout=3).json()
        info["ollama_version"] = v.get("version")
    except Exception as e:
        info["ollama_version_error"] = str(e)
    try:
        tags = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5).json()
        info["available_models"] = [m.get("model") for m in tags.get("models", [])]
    except Exception as e:
        info["available_models_error"] = str(e)
    return jsonify(info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
