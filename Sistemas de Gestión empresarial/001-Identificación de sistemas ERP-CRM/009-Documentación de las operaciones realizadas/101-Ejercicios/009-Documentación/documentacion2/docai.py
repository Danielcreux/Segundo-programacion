# docai.py - VERSIÓN OPTIMIZADA
import os, json, urllib.request
from typing import Dict, Optional

# Configuración optimizada
OPTIMIZED_MODEL = "qwen2.5-coder:1.5b"  # Modelo más pequeño y rápido
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TIMEOUT = 500  # 5 minutos máximo

def _http_post_json_optimized(url: str, payload: Dict) -> Dict:
    """Versión optimizada con timeout controlado"""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)

def build_project_context(root: str, allowed_exts=None, max_file_bytes=25000) -> str:
    """
    Contexto más compacto y rápido
    """
    lines = ["# 🗂️ CONTEXTO DEL PROYECTO (Resumen)\n"]
    
    for dirpath, _, files in os.walk(root):
        # Limitar profundidad
        rel_depth = len(os.path.relpath(dirpath, root).split(os.sep))
        if rel_depth > 3:
            continue
            
        rel = os.path.relpath(dirpath, root)
        lines.append(f"\n## 📁 {rel if rel != '.' else os.path.basename(root)}")
        
        for fname in sorted(files)[:10]:  # Máximo 10 archivos por carpeta
            ext = os.path.splitext(fname)[1].lstrip(".").lower()
            if allowed_exts and ext not in allowed_exts:
                continue
                
            path = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(path)
                if size > max_file_bytes:
                    lines.append(f"- 📄 {fname} ({size} bytes - demasiado grande)")
                    continue
                    
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(1000)  # Solo primeras 1000 líneas
                    
                lines.append(f"- 📄 {fname}")
                lines.append("  ```" + ext)
                lines.append("  " + "\n  ".join(content.split('\n')[:50]))  # Primeras 50 líneas
                lines.append("  ```")
                
            except Exception as e:
                lines.append(f"- 📄 {fname} (error: {str(e)})")
    
    return "\n".join(lines)

def document_code_with_ollama_optimized(filename: str, code: str, ext: str) -> str:
    """
    Versión optimizada para documentación individual
    """
    prompt = f"""Documenta brevemente este archivo en español:

ARCHIVO: {filename}
EXTENSIÓN: {ext}

CÓDIGO:
{code[:2000]}  # Limitar código

INSTRUCCIONES:
- Explica QUÉ HACE este archivo en 1-2 frases
- Identifica su FUNCIÓN principal
- Menciona elementos clave (3-5 puntos)
- Máximo 150 palabras
- Formato Markdown simple
"""
    
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
        payload = {
            "model": OPTIMIZED_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 2048,
                "num_predict": 300,
                "top_k": 20
            }
        }
        
        result = _http_post_json_optimized(url, payload)
        return result.get("response", "").strip()
        
    except Exception as e:
        return f"> 💡 *Documentación automática no disponible: {str(e)}*"

# Mantener compatibilidad
def document_code_with_ollama(*args, **kwargs):
    return document_code_with_ollama_optimized(*args, **kwargs)
