#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera resúmenes en español de todas las transcripciones en la carpeta 'transcripts/'.

Estructura esperada:
transcripts/
  ├── subcarpeta1/
  │     ├── video1.txt
  │     ├── video2.txt
  │     └── ...
  ├── subcarpeta2/
  │     ├── ...
  └── ...

Para cada archivo .txt:
- Lee el contenido completo.
- Lo envía a `ollama run qwen2.5:3b-instruct` para obtener un resumen en español.
- Guarda el resultado en `<nombre_original>.summary.txt` en la misma carpeta.
- Si el archivo de resumen ya existe, lo salta.

Requisitos:
  - Tener instalado ollama y el modelo qwen2.5:3b-instruct:
      ollama pull qwen2.5:3b-instruct
"""

import os
import subprocess
from pathlib import Path

# Carpeta raíz donde están las transcripciones
TRANSCRIPTS_ROOT = Path("transcripts")

# Modelo de Ollama
OLLAMA_MODEL = "qwen2.5:3b-instruct"

# Longitud máxima aproximada del texto que se manda al modelo
# (por si tus transcripciones son muy largas; si quieres, pon None para desactivar)
MAX_CHARS = 150000


def call_ollama_summarize(text: str) -> str:
    """
    Llama a 'ollama run qwen2.5:3b-instruct' pasando el prompt por stdin
    y devuelve la respuesta en texto plano.
    """
    prompt = f"""
Eres un asistente experto en educación y programación que resume transcripciones de vídeos en español.

A partir de la transcripción siguiente, escribe un resumen en ESPAÑOL que:
- Sea claro y conciso.
- Use entre 5 y 10 viñetas con los puntos clave.
- Termine con un breve párrafo final de síntesis.
- No invente contenido que no aparezca en la transcripción.
- Mantenga el tono docente y explicativo.

Transcripción:
\"\"\"{text}\"\"\"
"""

    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Error ejecutando ollama:\nSTDERR:\n{result.stderr.decode('utf-8', 'ignore')}"
        )

    return result.stdout.decode("utf-8", "ignore").strip()


def process_transcript_file(txt_path: Path) -> None:
    """
    Lee un .txt de transcripción, lo resume con ollama y guarda el
    resultado en .summary.txt en la misma carpeta.
    """
    summary_path = txt_path.with_suffix(".summary.txt")

    if summary_path.exists():
        print(f"[SKIP] Ya existe resumen: {summary_path}")
        return

    print(f"[PROC] {txt_path}")

    content = txt_path.read_text(encoding="utf-8", errors="ignore").strip()

    if not content:
        print(f"  · Archivo vacío, se omite.")
        return

    # Si quieres recortar transcripciones muy largas para evitar superar contexto:
    if MAX_CHARS is not None and len(content) > MAX_CHARS:
        print(f"  · Aviso: transcripción muy larga, recortando a {MAX_CHARS} caracteres.")
        content = content[:MAX_CHARS]

    try:
        summary = call_ollama_summarize(content)
    except Exception as e:
        print(f"  ✗ Error al resumir con ollama: {e}")
        return

    header = (
        f"RESUMEN GENERADO CON OLLAMA ({OLLAMA_MODEL})\n"
        f"ORIGINAL: {txt_path.name}\n"
        f"{'-'*60}\n\n"
    )

    summary_path.write_text(header + summary + "\n", encoding="utf-8")
    print(f"  ✓ Resumen guardado en: {summary_path}")


def main():
    if not TRANSCRIPTS_ROOT.is_dir():
        print(f"ERROR: No existe la carpeta '{TRANSCRIPTS_ROOT}'.")
        return

    print(f"Buscando transcripciones en: {TRANSCRIPTS_ROOT.resolve()}")

    count_total = 0
    count_done = 0

    # Recorre todas las subcarpetas y archivos
    for root, dirs, files in os.walk(TRANSCRIPTS_ROOT):
        root_path = Path(root)
        # Opcional: puedes saltarte carpetas de logs, etc., si quieres
        for fname in files:
            if not fname.lower().endswith(".txt"):
                continue
            if fname.lower().endswith(".summary.txt"):
                # No queremos re-resumir resúmenes
                continue

            txt_path = root_path / fname
            count_total += 1
            process_transcript_file(txt_path)
            count_done += 1

    print("\n=== RESUMEN GLOBAL ===")
    print(f"Archivos .txt encontrados (sin contar .summary.txt): {count_total}")
    print(f"Procesados (intento de resumen): {count_done}")


if __name__ == "__main__":
    main()
