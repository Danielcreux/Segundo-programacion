#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convierte un archivo de exportación de WhatsApp (Android o iOS) a un JSONL
en formato ChatML con pares pregunta–respuesta (Q&A).

- Lee INPUT_FILE (exportación de WhatsApp en texto).
- Detecta formato Android e iOS (incluyendo: [28/09/2023 10:15] Ana: ...).
- Reconstruye mensajes multilínea.
- Agrupa mensajes en bloques:
    usuarios (rol "user") -> asistente (rol "assistant")
- Genera OUTPUT_FILE en formato JSONL:

    {"messages":[
        {"role":"user","content":"..."},
        {"role":"assistant","content":"..."}
    ]}

Configura aquí:

    INPUT_FILE
    OUTPUT_FILE
    ASSISTANT_NAME
"""

import re
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# Archivos de entrada/salida
INPUT_FILE = "conversacion.txt"
OUTPUT_FILE = "conversacion.jsonl"

# Nombre de la persona que actúa como "asistente" en la conversación
ASSISTANT_NAME = "María"   # cámbialo si procede


# -----------------------------
# Patrones para reconocer INICIO de mensaje
# -----------------------------

# Android (español/Europa):
# 01/01/24, 9:15 - Nombre: mensaje
ANDROID_USER_RE = re.compile(
    r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - ([^:]+): (.*)$'
)

# Android sistema (sin "Nombre:"):
# 01/01/24, 9:15 - Mensaje del sistema...
ANDROID_SYSTEM_RE = re.compile(
    r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*)$'
)

# iOS usuario:
# [28/09/2023 10:15] Ana: mensaje
# [28/09/2023, 10:15] Ana: mensaje
IOS_USER_RE = re.compile(
    r'^\[(\d{1,2}/\d{1,2}/\d{2,4})[ ,]+(\d{1,2}:\d{2})\] ([^:]+): (.*)$'
)

# iOS sistema:
# [28/09/2023 10:15] Mensaje del sistema...
IOS_SYSTEM_RE = re.compile(
    r'^\[(\d{1,2}/\d{1,2}/\d{2,4})[ ,]+(\d{1,2}:\d{2})\] (.*)$'
)


def parse_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Intenta parsear la fecha y hora de WhatsApp a datetime.
    Acepta:
        "dd/mm/aa, HH:MM"
        "dd/mm/aaaa, HH:MM"
        "dd/mm/aa HH:MM"
        "dd/mm/aaaa HH:MM"
    """
    candidates = [
        f"{date_str}, {time_str}",
        f"{date_str} {time_str}",
    ]
    formats = [
        "%d/%m/%y, %H:%M",
        "%d/%m/%Y, %H:%M",
        "%d/%m/%y %H:%M",
        "%d/%m/%Y %H:%M",
    ]

    for candidate in candidates:
        for fmt in formats:
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue

    return None


def parse_new_message_line(line: str) -> Optional[Tuple[Optional[datetime], Optional[str], str]]:
    """
    Intenta interpretar una línea como inicio de un nuevo mensaje.

    Devuelve:
        (dt, author, text)
    donde author puede ser None para mensajes del sistema.

    Si la línea no parece un inicio de mensaje nuevo, devuelve None.
    """

    # Android con autor
    m = ANDROID_USER_RE.match(line)
    if m:
        date_str, time_str, author, text = m.groups()
        dt = parse_datetime(date_str, time_str)
        return dt, author.strip(), text

    # iOS con autor
    m = IOS_USER_RE.match(line)
    if m:
        date_str, time_str, author, text = m.groups()
        dt = parse_datetime(date_str, time_str)
        return dt, author.strip(), text

    # Android sistema
    m = ANDROID_SYSTEM_RE.match(line)
    if m:
        date_str, time_str, text = m.groups()
        dt = parse_datetime(date_str, time_str)
        return dt, None, text

    # iOS sistema
    m = IOS_SYSTEM_RE.match(line)
    if m:
        date_str, time_str, text = m.groups()
        dt = parse_datetime(date_str, time_str)
        return dt, None, text

    return None


def whatsapp_txt_a_mensajes(lines: List[str]) -> List[Dict]:
    """
    Convierte las líneas de un .txt de WhatsApp en una lista de mensajes estructurados.

    Cada mensaje:
    {
        "timestamp": datetime o None,
        "author": str o None (sistema),
        "text": str,
        "raw_line": str
    }
    """
    mensajes: List[Dict] = []
    actual: Optional[Dict] = None

    for raw_line in lines:
        line = raw_line.rstrip("\n\r")

        # Intentar detectar un nuevo mensaje
        parsed = parse_new_message_line(line)
        if parsed is not None:
            dt, author, text = parsed

            # Guardar el mensaje anterior si existía
            if actual is not None:
                mensajes.append(actual)

            # Crear nuevo mensaje
            actual = {
                "timestamp": dt,
                "author": author,
                "text": text if text is not None else "",
                "raw_line": line,
            }
        else:
            # Continuación de mensaje anterior (multilínea)
            if actual is not None:
                if actual["text"]:
                    actual["text"] += "\n" + line
                else:
                    actual["text"] = line
            else:
                # Línea fuera de cualquier mensaje (título, etc.). Se ignora.
                continue

    # Añadir último mensaje si existe
    if actual is not None:
        mensajes.append(actual)

    return mensajes


def mensajes_a_chatml_qna(mensajes: List[Dict]) -> List[Dict]:
    """
    A partir de la lista de mensajes "planos", genera pares Q&A
    en formato ChatML:

    {
      "messages": [
        {"role":"user", "content":"..."},
        {"role":"assistant", "content":"..."}
      ]
    }

    Lógica:
    - Se considera "assistant" cualquier mensaje cuyo author == ASSISTANT_NAME.
    - El resto de autores se consideran "user".
    - Se agrupan bloques:
        (uno o más mensajes de usuarios) seguido de (uno o más mensajes de asistente).
      Cada bloque genera un ejemplo Q&A.
    """
    # Filtrar mensajes de sistema (sin autor)
    msgs = [m for m in mensajes if m["author"] is not None]

    qna_examples: List[Dict] = []

    i = 0
    n = len(msgs)

    while i < n:
        m = msgs[i]
        # Si el mensaje actual es de la asistente sin bloque previo de usuario, se ignora
        if m["author"] == ASSISTANT_NAME:
            i += 1
            continue

        # Bloque de usuario(s): uno o más mensajes consecutivos de autores != ASSISTANT_NAME
        user_texts = [m["text"]]
        i += 1
        while i < n and msgs[i]["author"] != ASSISTANT_NAME:
            user_texts.append(msgs[i]["text"])
            i += 1

        # A continuación debería venir la asistente
        if i >= n or msgs[i]["author"] != ASSISTANT_NAME:
            # No hay respuesta de la asistente; no formamos Q&A
            continue

        # Bloque de asistente(s): uno o más mensajes consecutivos de author == ASSISTANT_NAME
        assistant_texts = [msgs[i]["text"]]
        i += 1
        while i < n and msgs[i]["author"] == ASSISTANT_NAME:
            assistant_texts.append(msgs[i]["text"])
            i += 1

        user_content = "\n".join(user_texts).strip()
        assistant_content = "\n".join(assistant_texts).strip()

        if not user_content or not assistant_content:
            continue

        example = {
            "messages": [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content},
            ]
        }
        qna_examples.append(example)

    return qna_examples


def escribir_jsonl_chatml_qna(examples: List[Dict], out_path: str) -> None:
    """
    Escribe la lista de ejemplos ChatML Q&A en un JSONL.
    """
    with open(out_path, "w", encoding="utf-8") as f_out:
        for ex in examples:
            f_out.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    print(f"Leyendo: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as f_in:
        lines = f_in.readlines()

    mensajes = whatsapp_txt_a_mensajes(lines)
    print(f"Mensajes totales parseados: {len(mensajes)}")

    qna_examples = mensajes_a_chatml_qna(mensajes)
    print(f"Pares Q&A generados: {len(qna_examples)}")

    escribir_jsonl_chatml_qna(qna_examples, OUTPUT_FILE)

    print(f"JSONL ChatML Q&A generado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

