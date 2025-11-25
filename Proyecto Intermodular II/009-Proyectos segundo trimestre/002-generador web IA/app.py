from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def call_ollama(prompt: str) -> str:
    """
    Call local Ollama with Qwen2.5-Coder and return the generated HTML+CSS.
    """
    # You can tune this system-style prefix to control what the model outputs
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
        # Ollama's /generate returns {"response": "...", "done": true, ...}
        return data.get("response", "").strip()
    except Exception as e:
        print("Error calling Ollama:", e)
        # Fallback: simple error page in HTML
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Error</title>
    <style>
        body {{ font-family: sans-serif; background:#2b2b2b; color:#f5f5f5; padding:2rem; }}
        .error {{ color:#ff6b6b; font-weight:bold; }}
    </style>
</head>
<body>
    <h1>Ooops…</h1>
    <p class="error">No se ha podido generar la página con la IA.</p>
    <p>Detalles técnicos: {e}</p>
</body>
</html>
        """


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    html = call_ollama(prompt)
    return jsonify({"html": html})


if __name__ == "__main__":
    # Run Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)

