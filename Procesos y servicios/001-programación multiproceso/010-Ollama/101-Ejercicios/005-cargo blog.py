import subprocess
import json
import os

SCHEMA_PATH = "blog.sql"
MAX_SCHEMA_CHARS = 200_000  # por si el .sql es enorme, evita pasarte de contexto

def cargar_schema_sql(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        schema = f.read()
    if len(schema) > MAX_SCHEMA_CHARS:
        schema = schema[:MAX_SCHEMA_CHARS] + "\n-- [Truncado para no exceder el contexto]\n"
    return schema

# Pide el prompt dinámicamente (o reemplázalo por una variable)
prompt_usuario = input("Introduce el prompt: ").strip()

# Carga el esquema de blog.sql
schema_sql = cargar_schema_sql(SCHEMA_PATH)

# Construye el contexto a inyectar en el prompt
contexto_sql = ""
if schema_sql:
    contexto_sql = (
        "Eres un asistente experto en SQL. A continuación tienes el esquema de base de datos "
        "extraído del archivo 'blog.sql'. Usa **exclusivamente** esta estructura para responder "
        "preguntas y proponer consultas SQL (estándar ANSI cuando sea posible). "
        "Responde siempre con:\n"
        "1) Breve explicación\n"
        "2) La consulta SQL dentro de un bloque ```sql```.\n\n"
        "=== ESQUEMA (blog.sql) ===\n"
        f"{schema_sql}\n"
        "=== FIN DEL ESQUEMA ===\n\n"
    )
else:
    contexto_sql = (
        "Eres un asistente experto en SQL. (Aviso: no se encontró 'blog.sql', responde de forma "
        "general sin validar contra un esquema cargado.)\n\n"
    )

# Prompt final que se envía al modelo
prompt_final = (
    f"{contexto_sql}"
    f"Pregunta del usuario:\n{prompt_usuario}\n"
)

# Construye el payload para Ollama
payload = {
    "model": "qwen3-coder:480b-cloud",
    "prompt": prompt_final,
    # Opcionalmente puedes fijar 'stream': True/False; por defecto es True y devolvemos JSONL
    # "stream": True
    # También puedes añadir un 'system' si prefieres separar instrucciones:
    # "system": "Sigue estrictamente el esquema proporcionado y el formato de salida indicado."
}

# Ejecuta la llamada curl
result = subprocess.run(
    [
        "curl", "-s", "http://localhost:11434/api/generate",
        "-d", json.dumps(payload)
    ],
    capture_output=True,
    text=True
)

# Parseo estilo jq + tr
try:
    lines = result.stdout.splitlines()
    response = ""
    for line in lines:
        if not line.strip():
            continue
        obj = json.loads(line)
        if "response" in obj and obj["response"] is not None:
            response += obj["response"]
    print(response.strip())
except Exception as e:
    print("Error parsing output:", e)
    print(result.stdout)

