import os
import re
import json
import requests
import mysql.connector
from functools import lru_cache
from flask import Flask, request, render_template_string, session, redirect, url_for, flash, jsonify

# ===================== CONFIG =====================
# ---- MySQL (edita estas credenciales) ----
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "crimson"),
    "password": os.environ.get("MYSQL_PASSWORD", "crimson"),
    "database": os.environ.get("MYSQL_DATABASE", "crimson"),
    "connection_timeout": 5,
}

# ---- Ollama ----
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
# Usa un modelo que TÚ ya tienes (según tu `ollama list`)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

# ---- Esquema & límites ----
SCHEMA_PATH = os.environ.get("SCHEMA_PATH", "aplicacion.sql")
MAX_SCHEMA_CHARS = 80_000
DEFAULT_LIMIT = int(os.environ.get("DEFAULT_LIMIT", "200"))
MAX_EXEC_MS = int(os.environ.get("MAX_EXEC_MS", "1500"))  # 1.5 s
MAX_ANALYSIS_ROWS = int(os.environ.get("MAX_ANALYSIS_ROWS", "50"))  # filas máx. para comentar

# ---- Flask ----
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
# Limpia siempre el historial al hacer nueva consulta
CLEAR_ON_NEW_QUERY = True
# ==================================================

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
    examples = (
        "### Formato estricto\n"
        "Responde SOLO con:\n"
        "1) 1-2 frases de explicación\n"
        "2) Un ÚNICO SELECT dentro de ```sql```\n"
        "Tras el bloque, escribe ENDSQL en una nueva línea.\n\n"
        "### Ejemplo\n"
        "Explicación: Últimos 10 clientes por Identificador.\n"
        "```sql\n"
        "SELECT * FROM clientes ORDER BY Identificador DESC LIMIT 10\n"
        "```\n"
        "ENDSQL\n"
    )
    contexto = (
        "Eres un asistente SQL extremadamente conciso. Usa EXCLUSIVAMENTE el esquema siguiente.\n"
        "Prohíbe DDL/DML. Prefiere LIMIT y filtros simples.\n\n"
        "=== ESQUEMA (compacto) ===\n"
        f"{schema_sql}\n"
        "=== FIN ESQUEMA ===\n\n"
        f"{examples}"
        f"Pregunta del usuario:\n{user_question}\n"
    )
    return contexto

def build_results_comment_prompt(question: str, sql: str, cols: list, rows: list, limit_rows: int) -> str:
    """
    Genera instrucciones para que el modelo comente/analice brevemente los resultados.
    Acotamos las filas para no inflar el contexto.
    """
    # Serializamos una vista compacta de resultados (máx. limit_rows)
    preview = []
    for r in rows[:limit_rows]:
        # Convertir posibles bytes/None a str seguros
        preview.append([("" if v is None else (v.decode() if isinstance(v, (bytes, bytearray)) else str(v))) for v in r])

    payload = {
        "question": question,
        "sql": sql,
        "columns": cols,
        "preview_rows": preview,
        "row_count_shown": min(len(rows), limit_rows),
        "row_count_total": len(rows),
    }
    return (
        "Actúa como analista de datos. Te paso una consulta SQL ejecutada y un avance de resultados.\n"
        "Objetivo: redacta 2-5 viñetas con **observaciones breves y útiles** (tendencias, valores extremos, conteos, medias/medianas aproximadas si son evidentes, advertencias de calidad de datos), en **máx. 80 palabras** en total.\n"
        "No inventes columnas ni cifras que no estén claras. Si faltan datos para una conclusión, dilo.\n\n"
        "### Contexto\n"
        f"Pregunta del usuario: {question}\n"
        f"SQL ejecutado:\n{sql}\n\n"
        "### Resultados (vista previa en JSON)\n"
        f"{json.dumps(payload, ensure_ascii=False) }\n"
    )

def ollama_healthcheck(base: str) -> None:
    try:
        r = requests.get(f"{base}/api/version", timeout=3)
        if r.status_code != 200:
            raise RuntimeError(
                f"Ollama respondió {r.status_code} en /api/version. "
                "¿URL correcta o proxy delante?"
            )
    except Exception as e:
        raise RuntimeError(
            f"No se puede conectar a Ollama en {base}. "
            "¿Ejecutaste `ollama serve` y el puerto 11434 está accesible? "
            f"Detalle: {e}"
        )

def call_ollama(prompt: str, *, temperature: float = 0.1, stop=None, num_predict: int = 160) -> str:
    """
    CHAT-ONLY: usa /api/chat para evitar 404 de /api/generate.
    Si el modelo no existe, devolvemos error claro con el payload del servidor.
    """
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
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": options,
        },
        timeout=300,
    )
    if r.status_code != 200:
        try:
            payload = r.json()
        except Exception:
            payload = {"error": r.text}
        # Error claro: normalmente {"error":"model 'xxx' not found"}
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
        if ln.lower().startswith("select "):
            return ln.strip().rstrip(";")
    return ""

def ensure_limit(sql: str, default_limit: int = DEFAULT_LIMIT) -> str:
    low = sql.lower()
    if " limit " in low:
        return sql
    if " count(" in low and " group by " not in low:
        return sql
    return f"{sql} LIMIT {default_limit}"

def add_max_exec_hint(sql: str, ms: int = MAX_EXEC_MS) -> str:
    return re.sub(r"(?is)\A(\s*select\s+)", rf"\1/*+ MAX_EXECUTION_TIME({ms}) */ ", sql, count=1)

def is_safe_select(sql: str) -> bool:
    lowered = f" {sql.lower()} "
    forbidden = [" insert ", " update ", " delete ", " drop ", " create ", " alter ", " truncate ", " grant ", " revoke ", " call ", " outfile ", " infile ", ";"]
    return " select " in lowered and not any(tok in lowered for tok in forbidden)

def run_select(sql: str):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(f"SET SESSION max_execution_time={MAX_EXEC_MS}")
        cur.execute(add_max_exec_hint(ensure_limit(sql)))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return cols, rows
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

# ---------- UI ----------
PAGE = """
<!doctype html>
<html lang="es" class="notranslate" translate="no">
<head>
  <meta charset="utf-8" />
  <title>AI SQL Chat · rápido</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root{
      --bg: #0b1220;
      --bg-soft: #111a2e;
      --card: #0f172a;
      --text: #e6e8ef;
      --muted: #9aa3b2;
      --accent: #6ea8fe;
      --accent-2: #7c4dff;
      --ok: #22c55e;
      --warn: #f59e0b;
      --err: #ef4444;
      --border: #20304f;
      --chip: #1b2550;
    }
    @media (prefers-color-scheme: light){
      :root{
        --bg:#f6f8fc; --bg-soft:#eef2ff; --card:#ffffff; --text:#1f2937; --muted:#5b6472;
        --accent:#2557D6; --accent-2:#6d28d9; --border:#e5e7eb; --chip:#eef2ff;
      }
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      color: var(--text);
      background: radial-gradient(1200px 600px at 20% -10%, rgba(108,99,255,.18), transparent 60%),
                  radial-gradient(1000px 500px at 120% 10%, rgba(110,168,254,.18), transparent 60%),
                  var(--bg);
    }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 24px; }
    header{
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
      border-radius: 16px; padding: 18px 20px; color:white; box-shadow: 0 10px 30px rgba(0,0,0,.2);
    }
    header h1{ margin: 0 0 6px; font-size: 22px; letter-spacing:.2px }
    header .sub{ opacity:.95; font-size:14px }
    .meta{ display:flex; flex-wrap:wrap; gap:10px; margin-top:10px }
    .chip{ background: rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.25); padding:6px 10px; border-radius:999px; font-size:12px }
    .panel{
      background: var(--card); border:1px solid var(--border); border-radius:16px; padding:16px; margin-top:16px;
      box-shadow: 0 6px 18px rgba(0,0,0,.08);
    }
    form { display: flex; gap: 10px; margin: 8px 0 0; }
    input[type=text]{
      flex:1; padding:12px 14px; border:1px solid var(--border); border-radius:12px; background:var(--bg-soft); color:var(--text);
      outline:none;
    }
    input[type=text]::placeholder{ color:var(--muted) }
    button{
      padding:12px 14px; border-radius:12px; border:0; background: var(--accent); color:white; cursor:pointer; font-weight:600;
      transition: transform .05s ease, opacity .2s ease;
    }
    button:hover{ opacity:.95 }
    button:active{ transform: translateY(1px) }
    .row{ display:grid; grid-template-columns: 1.1fr .9fr; gap:16px; margin-top:16px }
    @media (max-width: 900px){ .row{ grid-template-columns: 1fr } }
    .bubble { padding: 14px; border-radius: 12px; }
    .assistant { background: #0e1528; border:1px solid var(--border) }
    .sql-block{
      position: relative; background: #0a0f1f; border:1px solid var(--border); padding:12px; border-radius:12px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre-wrap; color:#cbd5e1;
    }
    .copy-btn{
      position:absolute; top:8px; right:8px; background:var(--chip); border:1px solid var(--border); color:var(--text); font-size:12px; padding:4px 8px; border-radius:8px; cursor:pointer;
    }
    .insights{
      background: #0a1224; border:1px solid var(--border); padding:12px; border-radius:12px; color:#dbeafe;
    }
    .insights h3{ margin: 0 0 8px; font-size:14px; letter-spacing:.2px; color:#93c5fd }
    .tags{ display:flex; gap:8px; margin-top:8px; flex-wrap:wrap }
    .tag{ background: var(--chip); border:1px solid var(--border); color:var(--text); font-size:11px; padding:4px 8px; border-radius:999px }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 14px; }
    thead th { position: sticky; top: 0; background: #0b1630; color:#d1d5db; z-index:1; }
    th, td { border: 1px solid var(--border); padding: 8px 10px; text-align: left; }
    tbody tr:nth-child(odd){ background: #0b1120 }
    tbody tr:hover{ background: #0f1530 }
    .flash { background: rgba(245, 158, 11, .15); border: 1px solid #f59e0b66; padding: 10px 12px; border-radius: 10px; margin: 8px 0; color:#fbbf24 }
    .error { background: rgba(239, 68, 68, .15); border: 1px solid #ef444466; color:#fecaca }
    .tiny { font-size: 12px; color: var(--muted); }
    footer{ margin-top:18px; color:var(--muted); font-size:12px; display:flex; gap:10px; flex-wrap:wrap }
    .pill{ padding:4px 8px; border-radius:999px; background:var(--chip); border:1px solid var(--border) }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>AI SQL Chat</h1>
      <div class="sub">Consultas rápidas, límite por defecto, SELECT seguro y comentarios automáticos.</div>
      <div class="meta">
        <div class="chip">BD: <b>{{ db }}</b></div>
        <div class="chip">Modelo: <code>{{ model }}</code></div>
        <div class="chip">Límite por defecto: {{ dlimit }}</div>
        <div class="chip">Máx. {{ ms }} ms</div>
        <div class="chip">Esquema: {{ schema_path }}</div>
        <div class="chip"><a style="color:white;" href="{{ url_for('health') }}">/health</a></div>
      </div>
      <form method="post" action="{{ url_for('chat') }}">
        <input type="text" name="q" placeholder="Ej: 'clientes de Valencia', 'últimos pedidos', 'precio medio de productos'…" required>
        <button type="submit">Preguntar</button>
      </form>
    </header>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for m in messages %}
          <div class="panel flash">{{ m }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if history %}
      {% for turn in history %}
        <div class="row">
          <div class="panel">
            <div class="bubble assistant">
              <div class="tiny">Pregunta</div>
              <div style="font-size:16px; margin-top:4px"><b>{{ turn.user }}</b></div>
            </div>

            <div class="bubble assistant" style="margin-top:10px">
              {% if turn.explain %}
                <div class="tiny">Explicación breve</div>
                <div style="margin-top:4px">{{ turn.explain }}</div>
              {% endif %}
              {% if turn.sql %}
                <div class="tiny" style="margin-top:12px">Consulta generada</div>
                <div class="sql-block">
                  <button class="copy-btn" onclick="copySQL(this)">Copiar</button>
                  <code>{{ turn.sql }}</code>
                </div>
                <div class="tags">
                  <span class="tag">Solo-lectura</span>
                  <span class="tag">MAX_EXECUTION_TIME={{ ms }}ms</span>
                  <span class="tag">LIMIT aplicado</span>
                </div>
              {% endif %}
              {% if turn.error %}
                <div class="flash error" style="margin-top:10px">{{ turn.error }}</div>
              {% endif %}
            </div>

            {% if turn.commentary %}
              <div class="insights" style="margin-top:10px">
                <h3>Comentario del asistente</h3>
                {{ turn.commentary|safe }}
              </div>
            {% endif %}
          </div>

          <div class="panel">
            {% if turn.cols is not none and turn.rows is not none %}
              <div class="tiny">Resultados ({{ turn.rows|length }} fila{{ '' if turn.rows|length == 1 else 's' }})</div>
              <div style="max-height: 480px; overflow:auto; border-radius:10px; margin-top:6px">
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
          </div>
        </div>
      {% endfor %}
    {% endif %}

    <footer>
      <div class="pill">Consejo: pide “desglose por mes” o “top 10 por total” para segmentaciones rápidas.</div>
      <div class="pill">Evita consultas pesadas: se corta a {{ dlimit }} filas y {{ ms }} ms.</div>
    </footer>
  </div>

  <script>
    function copySQL(btn){
      const code = btn.parentElement.querySelector('code').innerText;
      navigator.clipboard.writeText(code).then(()=>{
        btn.textContent = 'Copiado ✓';
        setTimeout(()=>btn.textContent='Copiar', 1200);
      });
    }
  </script>
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
        flash("Escribe una pregunta.")
        return redirect(url_for("index"))

    # 1) Mostrar solo la consulta actual
    if CLEAR_ON_NEW_QUERY:
        session["history"] = []
    else:
        session.setdefault("history", [])

    schema = cargar_schema_compacto(SCHEMA_PATH)

    # 1ª llamada LLM: Generar SQL
    try:
        llm_text = call_ollama(build_prompt(schema, q), stop=["ENDSQL"])
    except Exception as e:
        session["history"].append({
            "user": q, "explain": None, "sql": None, "cols": None, "rows": None,
            "commentary": None,
            "error": f"LLM falló: {e}"
        })
        session.modified = True
        return redirect(url_for("index"))

    explain = llm_text.split("```sql")[0].strip()
    sql = extract_sql_from_llm(llm_text)

    if not sql:
        session["history"].append({
            "user": q, "explain": explain, "sql": None, "cols": None, "rows": None,
            "commentary": None,
            "error": "No se pudo extraer una consulta SQL."
        })
        session.modified = True
        return redirect(url_for("index"))

    if not is_safe_select(sql):
        session["history"].append({
            "user": q, "explain": explain, "sql": sql, "cols": None, "rows": None,
            "commentary": None,
            "error": "Solo se permiten SELECT de solo lectura."
        })
        session.modified = True
        return redirect(url_for("index"))

    # Ejecutar SELECT
    try:
        cols, rows = run_select(sql)
        safe_sql = add_max_exec_hint(ensure_limit(sql))
        entry = {
            "user": q,
            "explain": explain,
            "sql": safe_sql,
            "cols": cols,
            "rows": rows,
            "commentary": None,
            "error": None
        }
        # 2ª llamada LLM: Comentario de resultados
        try:
            comment_prompt = build_results_comment_prompt(q, safe_sql, cols, rows, MAX_ANALYSIS_ROWS)
            comment_text = call_ollama(comment_prompt, temperature=0.2, num_predict=220)
            # Convertimos líneas a lista con viñetas si no vinieron ya
            if "- " in comment_text or "•" in comment_text:
                formatted = "<ul>" + "".join(f"<li>{line.strip('•- ').strip()}</li>" for line in comment_text.splitlines() if line.strip()) + "</ul>"
            else:
                # separa por puntos si no hay viñetas
                bullets = [s.strip() for s in re.split(r"[•\-]\s+|(?<=\.)\s+", comment_text) if s.strip()]
                formatted = "<ul>" + "".join(f"<li>{b}</li>" for b in bullets[:5]) + "</ul>"
            entry["commentary"] = formatted
        except Exception as e2:
            entry["commentary"] = f"<div class='flash'>No se pudo generar comentario: {e2}</div>"

        session["history"].append(entry)

    except Exception as e:
        session["history"].append({
            "user": q,
            "explain": explain,
            "sql": add_max_exec_hint(ensure_limit(sql)),
            "cols": None,
            "rows": None,
            "commentary": None,
            "error": f"Error SQL: {e}"
        })

    session.modified = True
    return redirect(url_for("index"))

@app.route("/health")
def health():
    info = {"ollama_base": OLLAMA_BASE, "model": OLLAMA_MODEL, "schema_path": SCHEMA_PATH}
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
    # Puedes ajustar host/port por variables de entorno si quieres
    app.run(host="0.0.0.0", port=5000, debug=True)
