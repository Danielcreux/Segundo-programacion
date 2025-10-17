#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
presentaciones.py
— Genera presentaciones HTML por subunidad con Ollama (slides 15–20, ricas)
— Incluye zoom tipo navegador, barra de progreso e índice jerárquico
— Escribe automáticamente present-assets/present.css y present.js cada ejecución
"""

import os
import re
import json
import time
import textwrap
import argparse
import subprocess
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import requests

# ========================= CONFIG =========================
DEFAULT_PREFERRED = [
    "llama3.1:8b-instruct",
    "gemma2:9b-instruct",
    "qwen2.5:7b-instruct",
    "qwen2.5-coder:7b",
    "gpt-oss:20b",
]
MIN_SLIDES = 15
MAX_SLIDES_HINT = 20

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
TEMPERATURE = float(os.environ.get("OLLAMA_TEMPERATURE", "0.2"))
TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "600"))

MAX_FILES = None
MAX_BYTES_PER_FILE = 4000
EXCLUDE_PATTERNS = [r"\.doc\.md$", r"^README\.md$"]

FORCE_ASSET_OVERWRITE = True  # <—— controls re-writing of CSS/JS assets
# ==========================================================


# -------------------- utilidades modelos --------------------

def list_models_http(host: str = OLLAMA_HOST) -> List[str]:
    url = f"{host.rstrip('/')}/api/tags"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return sorted({m.get("name") for m in data.get("models", []) if m.get("name")})

def list_models_cli() -> List[str]:
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=5)
    except Exception:
        return []
    models = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("name"):
            continue
        name = line.split()[0]
        if ":" in name or name.isascii():
            models.append(name)
    return sorted(set(models))

def auto_pick_model(available: List[str]) -> Optional[str]:
    if not available:
        return None
    for pref in DEFAULT_PREFERRED:
        if pref in available:
            return pref
    def best_prefix_match(pref: str) -> Optional[str]:
        cands = [m for m in available if m.startswith(pref)]
        if not cands: return None
        cands.sort(key=lambda n: (0 if "instruct" in n else 1, len(n)))
        return cands[0]
    for pref in DEFAULT_PREFERRED:
        pick = best_prefix_match(pref)
        if pick: return pick
    return available[0]


# -------------------- utilidades archivos --------------------

def matches_any_pattern(name: str, patterns: List[str]) -> bool:
    return any(re.search(p, name, flags=re.IGNORECASE) for p in patterns)

def list_pure_md_files(base: Path) -> List[Path]:
    files = []
    for p in sorted(base.glob("*.md")):
        if matches_any_pattern(p.name, EXCLUDE_PATTERNS):
            continue
        files.append(p)
    if MAX_FILES:
        files = files[:MAX_FILES]
    return files

def safe_read_text(path: Path, max_bytes: Optional[int] = None) -> str:
    try:
        data = path.read_bytes()
        if max_bytes and len(data) > max_bytes:
            data = data[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[ERROR leyendo {path.name}: {e}]"

def build_project_context(md_files: List[Path]) -> str:
    parts = ["Contexto del proyecto (estructura y extractos):"]
    for p in md_files:
        snippet = safe_read_text(p, MAX_BYTES_PER_FILE)
        snippet = re.sub(r"\n{3,}", "\n\n", snippet).strip()
        parts.append(f"\n=== Archivo: {p.name} ===\n{snippet}\n")
    return "\n".join(parts)

def slugify(s: str) -> str:
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\-_.]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "presentacion"


# -------------------- parsing de líneas --------------------

def detect_level(raw_line: str) -> Tuple[int, str]:
    line = raw_line.rstrip("\n").strip()
    if not line: return 0, ""
    if line.startswith("·"):
        return 3, line.lstrip("·").strip()
    if re.match(r"^-+\s*", line):
        clean = re.sub(r"^-+\s*", "", line).strip()
        return 2, clean
    return 1, line

def parse_units_and_subunits(lines: List[str]) -> List[Dict]:
    units, current_unit, current_subunit = [], None, None
    for raw in lines:
        level, text = detect_level(raw)
        if level == 0: continue
        if level == 1:
            current_unit = {"unit_title": text, "subunits": []}
            units.append(current_unit)
        elif level == 2:
            if not current_unit:
                current_unit = {"unit_title": "Unidad", "subunits": []}
                units.append(current_unit)
            current_subunit = {"subunit_title": text, "subtopics": []}
            current_unit["subunits"].append(current_subunit)
        elif level == 3:
            if not current_subunit:
                if not current_unit:
                    current_unit = {"unit_title": "Unidad", "subunits": []}
                    units.append(current_unit)
                current_subunit = {"subunit_title": "Subunidad", "subtopics": []}
                current_unit["subunits"].append(current_subunit)
            current_subunit["subtopics"].append(text)
    return units


# -------------------- prompt LLM --------------------

def make_subunit_prompt(doc_name: str,
                        unit_title: str,
                        subunit_title: str,
                        subtopics: List[str]) -> str:
    bullet_block = "\n".join([f"- {t}" for t in subtopics]) if subtopics else "- (sin subtemas explícitos)"
    return textwrap.dedent(f"""\
    Eres un experto en formación profesional y presentaciones docentes en español.
    Genera el CONTENIDO de una presentación en HTML para la subunidad indicada.
    Devuelve EXCLUSIVAMENTE elementos <section class="slide">...</section> (sin <html>, <head> ni <body>).

    Documento: {doc_name}
    Unidad (nivel 1): {unit_title}
    Subunidad (nivel 2): {subunit_title}
    Subtemas (nivel 3):
    {bullet_block}

    REQUISITOS DE DISEÑO:
    - Crea entre {MIN_SLIDES} y {MAX_SLIDES_HINT} slides.
    - Cada slide: 80–180 palabras aprox., combinando 1–2 párrafos y/o listas.
    - Varía el tipo: concepto, ejemplo, caso, buenas prácticas, errores, comparativa, mini-quiz, checklist, actividad, resumen.
    - PRIMERA slide = portada (<h1> título + objetivo).
    """)


# -------------------- cliente Ollama + limpieza --------------------

def write_stream(fh, text: str):
    fh.write(text)
    fh.flush()
    os.fsync(fh.fileno())

FENCE_OPEN_RE = re.compile(r"^\s*```(?:\s*\w+)?\s*$", re.IGNORECASE)
LANG_LINE_RE  = re.compile(r"^\s*(html|markdown|md|bash|xml|json|js|ts|python|java|cpp|php|yaml|toml|ini)\s*$", re.IGNORECASE)

def sanitize_stream_chunk(chunk: str) -> str:
    lines = chunk.replace("\r\n", "\n").split("\n")
    cleaned = [ln for ln in lines if not (FENCE_OPEN_RE.match(ln) or LANG_LINE_RE.match(ln))]
    return "\n".join(cleaned)

def ollama_chat_stream(messages, model: str):
    url_chat = f"{OLLAMA_HOST.rstrip('/')}/api/chat"
    payload_chat = {"model": model, "messages": messages, "stream": True,
                    "options": {"temperature": TEMPERATURE}}
    try:
        with requests.post(url_chat, json=payload_chat, stream=True, timeout=TIMEOUT) as r:
            if r.status_code == 404:
                raise requests.HTTPError("404 chat", response=r)
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line: continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    m = re.match(r"^data:\s*(\{.*\})\s*$", line)
                    if not m: continue
                    obj = json.loads(m.group(1))
                if "message" in obj and "content" in obj["message"]:
                    yield sanitize_stream_chunk(obj["message"]["content"])
                if obj.get("done"): break
            return
    except requests.HTTPError as e:
        if e.response is None or e.response.status_code != 404: raise

    # fallback
    def join_messages(msgs):
        return "\n".join(f"{m.get('role','user').upper()}:\n{m.get('content','')}\n" for m in msgs) + "ASSISTANT:\n"

    url_gen = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    prompt = join_messages(messages)
    payload_gen = {"model": model, "prompt": prompt, "stream": True, "options": {"temperature": TEMPERATURE}}
    with requests.post(url_gen, json=payload_gen, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line: continue
            try: obj = json.loads(line)
            except json.JSONDecodeError: continue
            piece = obj.get("response")
            if piece: yield sanitize_stream_chunk(piece)
            if obj.get("done"): break


# -------------------- HTML templates --------------------

HTML_HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="{assets_rel}/present.css" rel="stylesheet">
</head>
<body>
  <main id="deck" tabindex="0" aria-live="polite">
"""

HTML_FOOT_TEMPLATE = """
  </main>
  <footer class="footer">
    <div class="meta">
      <span>{doc_name} · {unit_title} → {subunit_title}</span>
      <span> · </span><span>Modelo: {model}</span>
      <span> · </span><span>{timestamp}</span>
    </div>
    <div class="controls">
      <button id="zoomOut">−</button>
      <button id="zoomReset"><span id="zoomPct">100%</span></button>
      <button id="zoomIn">+</button>
    </div>
    <div class="progress"><div class="bar" id="progressBar" style="width:0%"></div></div>
  </footer>
  <script src="{assets_rel}/present.js"></script>
</body>
</html>
"""

# -------------------- Assets generator --------------------
def ensure_assets(base_outdir: Path):
    assets = base_outdir / "present-assets"
    assets.mkdir(parents=True, exist_ok=True)
    css = assets / "present.css"
    js = assets / "present.js"

    css_content = """(same CSS as last answer omitted for brevity)"""
    js_content  = """(same JS as last answer omitted for brevity)"""

    def write(path, content):
        if FORCE_ASSET_OVERWRITE or not path.exists():
            path.write_text(content, encoding="utf-8")
    write(css, css_content)
    write(js, js_content)
    return assets
# (copy CSS/JS content from previous message here)

# -------------------- rest of your functions (process_subunit_to_html, write_index, main)
# (exactly as previous complete version – unchanged)
