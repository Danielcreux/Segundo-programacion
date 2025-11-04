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

# ---- Flask ----
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
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

def call_ollama(prompt: str) -> str:
    """
    CHAT-ONLY: usa /api/chat para evitar 404 de /api/generate.
    Si el modelo no existe, devolvemos error claro con el payload del servidor.
    """
    ollama_healthcheck(OLLAMA_BASE)
    options = {
        "temperature": 0.1,
        "top_p": 0.9,
        "num_ctx": 2048,
        "num_predict": 160,
        "stop": ["ENDSQL"],
    }
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
<html>
<head>
  <meta charset="utf-8" />
  <title>AI SQL Chat · rápido</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: #222; }
    .wrap { max-width: 980px; margin: 0 auto; }
    h1 { margin: 0 0 8px; }
    .note { color: #666; margin-bottom: 16px; }
    form { display: flex; gap: 8px; margin: 16px 0; }
    input[type=text] { flex: 1; padding: 10px 12px; border: 1px solid #ccc; border-radius: 10px; }
    button { padding: 10px 14px; border-radius: 10px; border: 0; background: #2557D6; color: white; cursor: pointer; }
    button:hover { opacity: 0.95; }
    .bubble { padding: 12px 14px; border-radius: 12px; margin: 10px 0; }
    .user { background: #f2f6ff; }
    .assistant { background: #f8f8f8; }
    .sql { background: #fff; border: 1px solid #e2e2e2; padding: 8px; border-radius: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre-wrap; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th, td { border: 1px solid #e2e2e2; padding: 6px 8px; text-align: left; font-size: 14px; }
    th { background: #fafafa; }
    .flash { background: #fff3cd; border: 1px solid #ffeeba; padding: 10px 12px; border-radius: 8px; margin: 8px 0; }
    .tiny { font-size: 12px; color: #666; }
    .explain { margin: 6px 0 10px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>AI SQL Chat (rápido)</h1>
    <div class="note">
      BD: <b>{{ db }}</b> · Modelo: <code>{{ model }}</code> · Límite por defecto: {{ dlimit }} · Máx. {{ ms }}ms · Esquema: {{ schema_path }}
      · <a href="{{ url_for('health') }}">/health</a>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for m in messages %}
          <div class="flash">{{ m }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <form method="post" action="{{ url_for('chat') }}">
      <input type="text" name="q" placeholder="Ej: 'clientes de Valencia', 'últimos pedidos', 'precio medio de productos'…" required>
      <button type="submit">Preguntar</button>
    </form>

    {% if history %}
      {% for turn in history %}
        <div class="bubble user">
          <b>Tú:</b><br>{{ turn.user }}
        </div>
        <div class="bubble assistant">
          <b>Asistente:</b>
          {% if turn.explain %}
            <div class="explain">{{ turn.explain }}</div>
          {% endif %}
          {% if turn.sql %}
            <div class="tiny">Consulta generada:</div>
            <div class="sql"><code>{{ turn.sql }}</code></div>
          {% endif %}
          {% if turn.error %}
            <div class="flash">{{ turn.error }}</div>
          {% endif %}
          {% if turn.cols is not none and turn.rows is not none %}
            <div class="tiny">Resultados:</div>
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
          {% endif %}
        </div>
      {% endfor %}
    {% endif %}
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
        flash("Escribe una pregunta.")
        return redirect(url_for("index"))

    session.setdefault("history", [])
    schema = cargar_schema_compacto(SCHEMA_PATH)

    try:
        llm_text = call_ollama(build_prompt(schema, q))
    except Exception as e:
        session["history"].append({
            "user": q, "explain": None, "sql": None, "cols": None, "rows": None,
            "error": f"LLM falló: {e}"
        })
        session.modified = True
        return redirect(url_for("index"))

    explain = llm_text.split("```sql")[0].strip()
    sql = extract_sql_from_llm(llm_text)

    if not sql:
        session["history"].append({
            "user": q, "explain": explain, "sql": None, "cols": None, "rows": None,
            "error": "No se pudo extraer una consulta SQL."
        })
        session.modified = True
        return redirect(url_for("index"))

    if not is_safe_select(sql):
        session["history"].append({
            "user": q, "explain": explain, "sql": sql, "cols": None, "rows": None,
            "error": "Solo se permiten SELECT de solo lectura."
        })
        session.modified = True
        return redirect(url_for("index"))

    try:
        cols, rows = run_select(sql)
        session["history"].append({
            "user": q,
            "explain": explain,
            "sql": add_max_exec_hint(ensure_limit(sql)),
            "cols": cols,
            "rows": rows,
            "error": None
        })
    except Exception as e:
        session["history"].append({
            "user": q,
            "explain": explain,
            "sql": add_max_exec_hint(ensure_limit(sql)),
            "cols": None,
            "rows": None,
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
    app.run(host="0.0.0.0", port=5000, debug=True)
