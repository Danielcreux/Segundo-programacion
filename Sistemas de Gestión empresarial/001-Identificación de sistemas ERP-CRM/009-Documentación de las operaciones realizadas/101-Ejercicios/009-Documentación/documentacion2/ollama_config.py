# ollama_config.py - Configuración optimizada
import os
import json
import urllib.request
from typing import Dict

# Usar modelo más pequeño y rápido
OPTIMIZED_MODEL = "qwen2.5-coder:1.5b"  # Modelo más pequeño
# O alternativas: "codellama:7b" o "phi3:mini"

OLLAMA_HOST = "http://localhost:11434"
TIMEOUT = 300  # 5 minutos

def optimized_ollama_generate(prompt: str, model: str = OPTIMIZED_MODEL) -> str:
    """
    Versión optimizada con timeout más corto y modelo pequeño
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,      # Menor variabilidad
            "num_ctx": 4096,         # Contexto más pequeño
            "num_predict": 500,      # Respuestas más cortas
            "top_k": 20,
            "top_p": 0.9
        }
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            result = json.loads(body)
            return result.get("response", "").strip()
            
    except Exception as e:
        return f"> ⚠️ Error en documentación IA: {str(e)}"