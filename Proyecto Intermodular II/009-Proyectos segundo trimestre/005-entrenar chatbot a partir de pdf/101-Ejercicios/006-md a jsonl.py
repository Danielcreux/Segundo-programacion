#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de pares Q/A en formato JSONL a partir de transcripciones en texto plano o Markdown.

- Recorre todos los .txt y .md de INPUT_DIR.
- Trocea cada texto en bloques con solape.
- Para cada bloque lanza 2 prompts a Ollama:
    * Preguntas fáciles / introductorias.
    * Preguntas intermedias / avanzadas.
- Genera UN JSONL POR ARCHIVO de entrada en OUTPUT_DIR.
- Mantiene un log.json con la lista de ficheros ya procesados para no duplicar materiales.

Características extra:
- Comprueba al inicio si Ollama está accesible.
- Detecta automáticamente si debe usar /api/chat o /api/generate.
- Guarda las Q/A sobre la marcha (bloque a bloque) en el JSONL, sin esperar al final.

Requisitos:
- Ollama sirviendo en http://localhost:11434
- Modelo MODEL_NAME presente en Ollama.
"""

import os
import re
import json
import requests
from typing import List, Dict, Optional

# =========================
# CONFIGURACIÓN GENERAL
# =========================

# Carpetas de entrada y salida
INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"
LOG_FILE = os.path.join(OUTPUT_DIR, "log.json")

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
# Ajusta aquí el modelo que vayas a usar
MODEL_NAME = "gemma2:9b-instruct-q4_0"

# Estos se rellenarán en detect_ollama_mode()
OLLAMA_MODE: Optional[str] = None   # "chat" o "generate"
OLLAMA_URL: Optional[str] = None    # URL completa del endpoint elegido

# Troceado del texto
MAX_CHARS_PER_BLOCK = 3500  # tamaño objetivo de cada bloque
BLOCK_OVERLAP = 500         # solape entre bloques para no perder contexto

# Generación de Q/A
TEMPERATURE = 0.3           # baja = más estable
MAX_TOKENS = 512            # límite aproximado de tokens generados


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


def strip_markdown(text: str) -> str:
    """
    Elimina en lo posible el "ruido" de Markdown para dejar solo texto útil.

    - Quita bloques de código triple ``` ... ```
    - Quita código en línea `...`
    - Convierte enlaces [texto](url) en solo "texto"
    - Quita imágenes ![alt](url)
    - Quita cabeceras de Markdown (#, ##, ###)
    - Quita marcadores de lista iniciales (-, *, +) al inicio de línea
    - Quita negritas/cursivas (**texto**, *texto*, __texto__, _texto_)
    """

    # Bloques de código triple
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Código en línea `code`
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Imágenes ![alt](url)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)

    # Enlaces [texto](url) -> texto
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Cabeceras tipo #, ##, ### al inicio de línea
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

    # Marcadores de lista al inicio de línea: -, *, +
    text = re.sub(r"^[\-\*\+]\s+", "", text, flags=re.MULTILINE)

    # Negritas/cursivas: **texto**, *texto*, __texto__, _texto_
    text = text.replace("**", "").replace("__", "")
    text = text.replace("*", "").replace("_", "")

    return text


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
            "inputs/tema2.md",
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
# DETECCIÓN DEL MODO OLLAMA
# =========================

def detect_ollama_mode() -> bool:
    """
    Detecta si Ollama expone /api/chat o /api/generate y configura
    las variables globales OLLAMA_MODE y OLLAMA_URL.

    Devuelve True si alguno de los dos endpoints funciona, False si ninguno.
    """
    global OLLAMA_MODE, OLLAMA_URL

    # Primero probamos /api/chat
    chat_url = f"{OLLAMA_BASE_URL}/api/chat"
    print(f"[INFO] Probando endpoint: {chat_url}")
    try:
        payload_chat = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Responde con una sola palabra: OK"},
                {"role": "user", "content": "OK"}
            ],
            "stream": False
        }
        resp = requests.post(chat_url, json=payload_chat, timeout=10)

        if resp.status_code == 404:
            print("[INFO] /api/chat devuelve 404, se probará /api/generate.")
        else:
            resp.raise_for_status()
            data = resp.json()
            if "message" in data and "content" in data["message"]:
                print("[INFO] Endpoint /api/chat detectado correctamente.")
                OLLAMA_MODE = "chat"
                OLLAMA_URL = chat_url
                return True
            else:
                print("[WARN] /api/chat respondió pero no con el formato esperado.")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se puede conectar a Ollama en {OLLAMA_BASE_URL}")
        print("       ¿Está arrancado? Ejecuta:  ollama serve")
        return False
    except Exception as e:
        print(f"[WARN] Error al probar /api/chat: {e}")

    # Si /api/chat no sirve, probamos /api/generate
    gen_url = f"{OLLAMA_BASE_URL}/api/generate"
    print(f"[INFO] Probando endpoint: {gen_url}")
    try:
        payload_gen = {
            "model": MODEL_NAME,
            "prompt": "Responde con una sola palabra: OK",
            "stream": False
        }
        resp = requests.post(gen_url, json=payload_gen, timeout=10)

        if resp.status_code == 404:
            print("[ERROR] /api/generate también devuelve 404.")
            print("[ERROR] Ninguno de los endpoints estándar de Ollama está disponible.")
            print("[ERROR] Revisa el nombre del modelo o si Ollama está arrancado.")
            print("       Modelo actual:", MODEL_NAME)
            return False

        resp.raise_for_status()
        data = resp.json()
        if "response" in data:
            print("[INFO] Endpoint /api/generate detectado correctamente.")
            OLLAMA_MODE = "generate"
            OLLAMA_URL = gen_url
            return True
        else:
            print("[WARN] /api/generate respondió pero no con el formato esperado.")
            return False

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se puede conectar a Ollama en {OLLAMA_BASE_URL}")
        print("       ¿Está arrancado? Ejecuta:  ollama serve")
        return False
    except Exception as e:
        print(f"[ERROR] Error al probar /api/generate: {e}")
        return False


# =========================
# LLAMADA A OLLAMA (según modo detectado)
# =========================

def call_ollama(system_prompt: str, user_prompt: str) -> str:
    """
    Llama a Ollama usando el endpoint detectado (chat o generate).

    - En modo "chat": usa /api/chat con messages.
    - En modo "generate": concatena system_prompt + user_prompt en un solo prompt
      y llama a /api/generate.
    """
    if OLLAMA_MODE is None or OLLAMA_URL is None:
        raise RuntimeError("OLLAMA_MODE no está configurado. Llama antes a detect_ollama_mode().")

    if OLLAMA_MODE == "chat":
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS
            }
        }
    elif OLLAMA_MODE == "generate":
        full_prompt = f"""{system_prompt.strip()}

Usuario:
{user_prompt.strip()}
"""
        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS
            }
        }
    else:
        raise RuntimeError(f"Modo de Ollama desconocido: {OLLAMA_MODE}")

    resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()

    if OLLAMA_MODE == "chat":
        return data["message"]["content"]
    else:  # generate
        return data.get("response", "")


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
        # A veces el modelo añade viñetas, etc. Limpiamos.
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()

        # Asegurarse de que empieza por { y acaba en }
        if not (line.startswith("{") and line.endswith("}")):
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
# PROCESAMIENTO DE UN FICHERO (GUARDADO SOBRE LA MARCHA)
# =========================

def process_single_file(path: str, output_path: str) -> int:
    """
    Procesa un único fichero de entrada y va escribiendo las Q/A
    en JSONL sobre la marcha en output_path.

    Devuelve el número total de pares generados.
    """
    print(f"\n[INFO] Procesando archivo: {path}")
    raw_text = read_text_file(path)
    if not raw_text.strip():
        print("[WARN] Archivo vacío, se ignora.")
        return 0

    # 1) Limpiar Markdown
    cleaned = strip_markdown(raw_text)
    # 2) Normalizar espacios
    text = normalize_whitespace(cleaned)

    if not text.strip():
        print("[WARN] Tras limpiar Markdown el archivo quedó vacío, se ignora.")
        return 0

    blocks = split_into_blocks(text)
    print(f"[INFO] Texto troceado en {len(blocks)} bloques.")

    # Truncar el fichero de salida al inicio, por si existe de ejecuciones anteriores
    with open(output_path, "w", encoding="utf-8") as f:
        pass

    total_pairs_for_file = 0

    for i, block in enumerate(blocks, start=1):
        print(f"[INFO]   Bloque {i}/{len(blocks)} (longitud {len(block)} chars)")

        block_pairs = generate_qa_for_block(block)
        print(f"[INFO]   -> {len(block_pairs)} pares Q/A generados para este bloque.")

        # Guardar inmediatamente en el JSONL
        if block_pairs:
            with open(output_path, "a", encoding="utf-8") as f:
                for p in block_pairs:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

        total_pairs_for_file += len(block_pairs)

    print(f"[INFO] Total pares Q/A para {os.path.basename(path)}: {total_pairs_for_file}")
    return total_pairs_for_file


# =========================
# MAIN
# =========================

def main():
    ensure_dirs()

    print("[INFO] Comprobando servicio de Ollama y detectando endpoint...")
    if not detect_ollama_mode():
        print("[FATAL] No se ha podido detectar un endpoint válido de Ollama. Abortando.")
        return

    input_files = [
        os.path.join(INPUT_DIR, fn)
        for fn in os.listdir(INPUT_DIR)
        if fn.lower().endswith((".txt", ".md"))
    ]

    if not input_files:
        print(f"[INFO] No se han encontrado .txt ni .md en {INPUT_DIR}.")
        print("      Crea la carpeta y coloca tus transcripciones allí.")
        return

    log = load_log()
    processed_files = set(log.get("processed_files", []))

    total_pairs = 0
    newly_processed_count = 0
    skipped_count = 0

    for path in sorted(input_files):
        if path in processed_files:
            print(f"[INFO] Archivo ya procesado según log.json, se omite: {path}")
            skipped_count += 1
            continue

        base_name = os.path.splitext(os.path.basename(path))[0]
        per_file_output = os.path.join(OUTPUT_DIR, f"{base_name}.jsonl")

        pairs_count = process_single_file(path, per_file_output)
        total_pairs += pairs_count

        log.setdefault("processed_files", []).append(path)
        save_log(log)
        processed_files.add(path)
        newly_processed_count += 1

        print(f"[INFO] JSONL generado para {path}: {per_file_output}")

    print("\n[RESUMEN]")
    print(f"Archivos encontrados              : {len(input_files)}")
    print(f"Archivos ya procesados (skip)     : {skipped_count}")
    print(f"Archivos procesados en esta run   : {newly_processed_count}")
    print(f"Pares Q/A generados en esta run   : {total_pairs}")
    print(f"Log de materiales procesados      : {LOG_FILE}")
    print(f"JSONL individuales en             : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

