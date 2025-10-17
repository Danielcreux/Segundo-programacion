# docai.py (extended with project context)
import os, json, urllib.request
from typing import Dict, Optional

DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

# ========== HTTP helper ==========
def _http_post_json(url: str, payload: Dict, timeout: int = 120) -> Dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)

# ========== Build project snapshot ==========
def build_project_context(root: str,
                          allowed_exts=None,
                          max_file_bytes=50_000) -> str:
    """
    Traverse the project folder and return a Markdown snapshot
    of structure + file contents (capped).
    """
    lines = []
    for dirpath, _, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        lines.append(f"\n## 📁 {rel if rel != '.' else root}")
        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lstrip(".").lower()
            if allowed_exts and ext not in allowed_exts:
                continue
            path = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(path)
                with open(path, "rb") as fh:
                    raw = fh.read(min(size, max_file_bytes))
                content = raw.decode("utf-8", errors="replace")
                lines.append(f"\n### 📄 {fname}")
                lines.append("```" + ext)
                lines.append(content)
                if size > max_file_bytes:
                    lines.append(f"... [truncated after {max_file_bytes} bytes]")
                lines.append("```")
            except Exception as e:
                lines.append(f"\n### 📄 {fname} (no leído: {e})")
    return "\n".join(lines)

# ========== Prompt builder ==========
def _build_prompt(project_context: str, filename: str, ext: str, code: str) -> str:
    return f"""Eres un asistente técnico.

A continuación tienes una instantánea del PROYECTO COMPLETO, con su estructura de carpetas y contenidos relevantes:

<PROYECTO>
{project_context}
</PROYECTO>

Ahora concéntrate en este archivo:

ARCHIVO: {filename}  (extensión: {ext})
CÓDIGO:
{code}

Tarea:
- Explica qué hace este archivo.
- Indica su papel dentro del proyecto global.
- Menciona dependencias y relaciones con otros archivos.
- Usa Markdown en español (breve, claro, máximo 10 viñetas).
- No repitas código, solo explica y documenta.
"""

# ========== Call Ollama ==========
def ollama_generate(prompt: str,
                    model: str = DEFAULT_MODEL,
                    host: str = DEFAULT_OLLAMA_HOST,
                    timeout: int = 600) -> str:
    url = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 800}
    }
    res = _http_post_json(url, payload, timeout)
    return (res.get("response") or "").strip()

# ========== Public API ==========
def document_code_with_project(filename: str,
                               code: str,
                               ext: str,
                               project_context: str,
                               model: str = DEFAULT_MODEL,
                               host: str = DEFAULT_OLLAMA_HOST) -> str:
    prompt = _build_prompt(project_context, filename, ext, code)
    try:
        return ollama_generate(prompt, model=model, host=host)
    except Exception as e:
        return f"> ⚠️ Error llamando a Ollama: {e}"


