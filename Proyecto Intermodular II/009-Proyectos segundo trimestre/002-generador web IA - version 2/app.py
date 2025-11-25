from flask import Flask, render_template, request, jsonify, send_file
import requests
from zipfile import ZipFile
import os
import io
import datetime
import base64

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3-coder:480b-cloud"

# Guardaremos el último HTML generado
LAST_GENERATED_HTML = ""


def call_ollama(prompt: str) -> str:
    system_instruction = """
You are an AI that generates HTML and CSS only.

Requirements:
- Return a complete HTML document.
- Include CSS either inline or inside a <style> tag in the <head>.
- Do NOT include any <script> tags or JavaScript code.
- Do NOT include explanations or comments in natural language.
- Just respond with the pure HTML (and embedded CSS).
"""

    full_prompt = f"""{system_instruction}

User requirement:
{prompt}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except Exception as e:
        print("Error calling Ollama:", e)
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Error</title>
</head>
<body>
    <h1>Error generando página</h1>
    <p>{e}</p>
</body>
</html>
        """


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    global LAST_GENERATED_HTML

    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    html = call_ollama(prompt)
    LAST_GENERATED_HTML = html

    return jsonify({"html": html})


# -----------------------------
# Descargar ZIP con HTML + CSS
# -----------------------------
@app.route("/download_project", methods=["POST"])
def download_project():
    global LAST_GENERATED_HTML

    if not LAST_GENERATED_HTML:
        return jsonify({"error": "No HTML generated"}), 400

    title = request.json.get("title", "landing")
    title = title.replace(" ", "_").lower()

    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    folder_name = f"{title}_{date_str}"

    zip_buffer = io.BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr(f"{folder_name}/index.html", LAST_GENERATED_HTML)
        zip_file.writestr(f"{folder_name}/style.css", "/* You may extract CSS manually if needed */")

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{folder_name}.zip"
    )


# -----------------------------
# Descargar captura WebP
# -----------------------------
@app.route("/export_webp", methods=["POST"])
def export_webp():
    data = request.json.get("image")
    if not data:
        return jsonify({"error": "No image data"}), 400

    header, encoded = data.split(",", 1)
    img_bytes = base64.b64decode(encoded)

    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"landing_{date_str}.webp"

    return send_file(
        io.BytesIO(img_bytes),
        mimetype="image/webp",
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
