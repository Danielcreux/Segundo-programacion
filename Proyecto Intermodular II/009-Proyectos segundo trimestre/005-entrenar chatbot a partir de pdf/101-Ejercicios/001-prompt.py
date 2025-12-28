#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de pares Q/A en formato JSONL a partir de transcripciones en texto plano.

- Recorre todos los .txt de INPUT_DIR.
- Trocea cada texto en bloques con solape.
- Para cada bloque lanza 2 prompts a Ollama (Llama3 8B):
    * Preguntas fáciles / introductorias.
    * Preguntas intermedias / avanzadas.
- Genera UN JSONL POR ARCHIVO de entrada en OUTPUT_DIR.
- Mantiene un log.json con la lista de ficheros ya procesados para no duplicar materiales.

Pensado para funcionar con:
- Ubuntu 24.04
- Ollama sirviendo en http://localhost:11434
- Modelo llama3:8b (o similar) cargado en GPU (GTX 1660).
"""

import os
import json
import requests
from typing import List, Dict

# =========================
# CONFIGURACIÓN GENERAL
# =========================

# Carpetas de entrada y salida
INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"
LOG_FILE = os.path.join(OUTPUT_DIR, "log.json")

# Modelo de Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3:8b"   # ajusta si usas otro tag, p.ej. "llama3:8b-instruct"

# Troceado del texto
MAX_CHARS_PER_BLOCK = 3500  # tamaño objetivo de cada bloque
BLOCK_OVERLAP = 500         # solape entre bloques para no perder contexto

# Generación de Q/A
TEMPERATURE = 0.3           # baja = más estable
MAX_TOKENS = 512            # límite de generación aproximado (Ollama lo ajusta internamente)


# =========================
# UTILIDADES BÁSICAS
# =========================

def ensure_dirs():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def normalize_whitespace(text: str) -> str:
    # Quita espacios duplicados, saltos de línea raros, etc.
    return " ".join(text.split())


def split_into_blocks(text: str,
                      max_chars: int = MAX_CHARS_PER_BLOCK,
                      overlap: int = BLOCK_OVERLAP) -> List[str]:
    """
    Trocea el texto en bloques de tamaño aproximado `max_chars`,
    con un solape de `overlap` caracteres entre bloques consecutivos.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    blocks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_chars, n)

        # Intentar cortar cerca de un final de frase (., ?, !)
        split_pos = end
        for sep in [".", "?", "!", "¿", "¡"]:
            pos = text.rfind(sep, start + int(max_chars * 0.6), end)
            if pos != -1 and pos > start:
                split_pos = max(split_pos, pos + 1)

        if split_pos == end:  # no encontró nada razonable
            split_pos = end

        block = text[start:split_pos].strip()
        if block:
            blocks.append(block)

        if split_pos >= n:
            break

        # Retrocede un poco para crear solape
        start = max(0, split_pos - overlap)

    return blocks


# =========================
# GESTIÓN DEL LOG
# =========================

def load_log() -> Dict:
    """
    Carga el log de ficheros procesados.

    Estructura:
    {
        "processed_files": [
            "inputs/tema1.txt",
            "inputs/tema2.txt",
            ...
        ]
    }
    """
    if not os.path.exists(LOG_FILE):
        return {"processed_files": []}

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "processed_files" not in data or not isinstance(data["processed_files"], list):
            return {"processed_files": []}
        return data
    except Exception:
        # Si el log está corrupto, empezamos de cero para no bloquear el proceso.
        return {"processed_files": []}


def save_log(log: Dict):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


# =========================
# LLAMADA A OLLAMA
# =========================

def call_ollama(system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        # "options": {"num_ctx": 2048, ...}  # opcional
    }

    resp = requests.post(OLLAMA_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"]


# =========================
# PROMPTS PARA Q/A
# =========================

SYSTEM_PROMPT_QA = """
Eres un generador de preguntas y respuestas de alta calidad en español
para entrenar un modelo de lenguaje educativo.

Tu tarea:
- Leer con mucha atención un bloque de transcripción técnica en español.
- Identificar TODOS los conceptos importantes posibles (términos, pasos, advertencias,
  decisiones de diseño, buenas prácticas, errores habituales, matices, etc.).
- A partir de esos conceptos, generar muchas preguntas y respuestas útiles para entrenamiento.

Reglas generales:
- No inventes conceptos que no aparezcan o no se deduzcan claramente del texto.
- Las respuestas deben ser completas pero concisas, sin relleno.
- Siempre responde en español neutro.
- Usa el formato JSON Lines: cada línea un objeto JSON con campos:
  {"question": "...", "answer": "..."}
- No añadas texto fuera de ese formato (ni comentarios, ni encabezados).
- No pongas comas finales después del objeto JSON en cada línea.
""".strip()


def build_user_prompt_easy(block: str) -> str:
    """
    Prompt para preguntas fáciles / introductorias.
    """
    return f"""
Genera PREGUNTAS FÁCILES (nivel introductorio) con sus respuestas a partir del siguiente texto.

Requisitos:
- Preguntas de tipo:
  * definición (¿qué es...?),
  * propósito (¿para qué sirve...?),
  * pasos básicos (¿cuál es el primer paso para...?),
  * identificación (¿qué nombre recibe...?),
  * ventajas / desventajas claras.
- Cubre todos los conceptos básicos que veas.
- Intenta generar muchas preguntas (por ejemplo, 10-20 por bloque si el texto lo permite,
  o más si hay muchos conceptos).
- Formato OBLIGATORIO: JSON Lines, cada línea:
  {{"question": "texto de la pregunta", "answer": "texto de la respuesta"}}

Texto:
\"\"\"{block}\"\"\"
""".strip()


def build_user_prompt_advanced(block: str) -> str:
    """
    Prompt para preguntas intermedias / avanzadas.
    """
    return f"""
Genera PREGUNTAS INTERMEDIAS y AVANZADAS con sus respuestas a partir del siguiente texto.

Requisitos:
- Preguntas de tipo:
  * razonamiento (¿por qué es recomendable...?, ¿qué ocurre si no se hace...?),
  * comparación (¿qué diferencia hay entre... y ...?),
  * casos prácticos (¿qué harías si...?, ¿en qué situación conviene...?),
  * consecuencias (¿qué puede pasar si...?, ¿qué problema se evita al...?),
  * buenas prácticas y advertencias.
- Exprime al máximo el contenido: si hay muchos matices, genera muchas preguntas.
- Puedes reutilizar un mismo concepto con enfoques distintos.
- Formato OBLIGATORIO: JSON Lines, cada línea:
  {{"question": "texto de la pregunta", "answer": "texto de la respuesta"}}

Texto:
\"\"\"{block}\"\"\"
""".strip()


# =========================
# PARSEO SEGURO DEL JSONL
# =========================

def parse_jsonl_from_llm(text: str) -> List[Dict[str, str]]:
    """
    Intenta extraer líneas JSON válidas del texto devuelto por el modelo.
    Ignora líneas vacías o mal formadas.
    """
    pairs = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # A veces el modelo añade viñetas, intents, etc. Intentamos limpiar.
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()

        # Asegurarse de que empieza por { y acaba en }
        if not (line.startswith("{") and line.endswith("}")):
            # Intenta recortar desde el primer '{' hasta el último '}'
            if "{" in line and "}" in line:
                line = line[line.find("{"):line.rfind("}") + 1]
            else:
                continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        q = obj.get("question")
        a = obj.get("answer")
        if isinstance(q, str) and isinstance(a, str):
            pairs.append({"question": q.strip(), "answer": a.strip()})

    return pairs


# =========================
# LÓGICA PRINCIPAL POR BLOQUE
# =========================

def generate_qa_for_block(block: str) -> List[Dict[str, str]]:
    """
    Genera Q/A fáciles y avanzadas para un bloque.
    """
    all_pairs: List[Dict[str, str]] = []

    # Preguntas fáciles
    try:
        easy_text = call_ollama(
            SYSTEM_PROMPT_QA,
            build_user_prompt_easy(block)
        )
        easy_pairs = parse_jsonl_from_llm(easy_text)
        all_pairs.extend(easy_pairs)
    except Exception as e:
        print(f"[WARN] Error generando Q/A fáciles: {e}")

    # Preguntas intermedias / avanzadas
    try:
        adv_text = call_ollama(
            SYSTEM_PROMPT_QA,
            build_user_prompt_advanced(block)
        )
        adv_pairs = parse_jsonl_from_llm(adv_text)
        all_pairs.extend(adv_pairs)
    except Exception as e:
        print(f"[WARN] Error generando Q/A avanzadas: {e}")

    return all_pairs


# =========================
# PROCESAMIENTO DE UN FICHERO
# =========================

def process_single_file(path: str) -> List[Dict[str, str]]:
    print(f"\n[INFO] Procesando archivo: {path}")
    raw_text = read_text_file(path)
    if not raw_text.strip():
        print("[WARN] Archivo vacío, se ignora.")
        return []

    text = normalize_whitespace(raw_text)
    blocks = split_into_blocks(text)
    print(f"[INFO] Texto troceado en {len(blocks)} bloques.")

    file_pairs: List[Dict[str, str]] = []

    for i, block in enumerate(blocks, start=1):
        print(f"[INFO]   Bloque {i}/{len(blocks)} (longitud {len(block)} chars)")
        block_pairs = generate_qa_for_block(block)
        print(f"[INFO]   -> {len(block_pairs)} pares Q/A generados para este bloque.")
        file_pairs.extend(block_pairs)

    print(f"[INFO] Total pares Q/A para {os.path.basename(path)}: {len(file_pairs)}")
    return file_pairs


# =========================
# ESCRITURA DE SALIDA
# =========================

def write_pairs_to_jsonl(pairs: List[Dict[str, str]], output_path: str):
    """
    Escribe TODOS los pares en un JSONL (sobrescribe si ya existe).
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")


# =========================
# MAIN
# =========================

def main():
    ensure_dirs()

    txt_files = [
        os.path.join(INPUT_DIR, fn)
        for fn in os.listdir(INPUT_DIR)
        if fn.lower().endswith(".txt")
    ]

    if not txt_files:
        print(f"[INFO] No se han encontrado .txt en {INPUT_DIR}.")
        print("      Crea la carpeta y coloca tus transcripciones allí.")
        return

    log = load_log()
    processed_files = set(log.get("processed_files", []))

    total_pairs = 0
    newly_processed_count = 0
    skipped_count = 0

    for path in sorted(txt_files):
        if path in processed_files:
            print(f"[INFO] Archivo ya procesado según log.json, se omite: {path}")
            skipped_count += 1
            continue

        pairs = process_single_file(path)

        # Nombre del JSONL por archivo
        base_name = os.path.splitext(os.path.basename(path))[0]
        per_file_output = os.path.join(OUTPUT_DIR, f"{base_name}.jsonl")

        write_pairs_to_jsonl(pairs, per_file_output)
        total_pairs += len(pairs)

        # Actualizar log y guardar inmediatamente para no perder progreso
        log.setdefault("processed_files", []).append(path)
        save_log(log)
        processed_files.add(path)
        newly_processed_count += 1

        print(f"[INFO] JSONL generado para {path}: {per_file_output}")

    print("\n[RESUMEN]")
    print(f"Archivos encontrados              : {len(txt_files)}")
    print(f"Archivos ya procesados (skip)     : {skipped_count}")
    print(f"Archivos procesados en esta run   : {newly_processed_count}")
    print(f"Pares Q/A generados en esta run   : {total_pairs}")
    print(f"Log de materiales procesados      : {LOG_FILE}")
    print(f"JSONL individuales en             : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

