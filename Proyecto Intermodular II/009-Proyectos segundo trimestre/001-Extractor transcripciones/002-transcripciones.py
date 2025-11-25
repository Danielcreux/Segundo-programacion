#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transcribe español desde YouTube con yt-dlp (con fallback robusto).

Nueva lógica:
- Lee TODOS los JSON de la carpeta 'playlists_expandidas/' (un JSON por playlist).
- Cada JSON tiene:
    {
      "id": "<playlist_id>",
      "title": "<playlist_title>",
      "url": "https://www.youtube.com/playlist?list=...",
      "items": [
        { "id", "title", "url", "type": "video" },
        ...
      ]
    }
- Para cada playlist crea una carpeta dentro de 'transcripts/' con el nombre saneado.
- Genera un .txt por cada vídeo (y .log en caso de problemas) dentro de esa carpeta.

Lógica de subtítulos:
- Prueba player_client=mweb -> tv -> web -> android (android al final por PO token).
- Prioriza subtítulos en español (es, es-ES, es-419, es.*).
- Si no hay español: toma el primer auto-caption disponible (p.ej. 'en').
- Como rescate final: --all-subs y luego filtra el mejor candidato.
- Convierte .vtt a texto sólido (un párrafo) sin timestamps, etiquetas, ni roll-up.
- Registra en .log los idiomas disponibles si no se consigue nada.

Requisitos:
  pip install -U yt-dlp
  (opcional) cookies.txt válido (exportado del navegador)
"""

import json
import re
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Optional

# =======================
# CONFIG
# =======================
PLAYLISTS_DIR = Path("playlists_expandidas")  # entrada: JSON por playlist
OUT_BASE_DIR = Path("transcripts")            # salida: carpeta por playlist
SLEEP_BETWEEN = 2.0

COOKIES_FILE = Path("cookies.txt")  # cambia si lo tienes en otra ruta
USER_AGENT = "Mozilla/5.0"

# Ponemos android al final para evitar el problema del PO token si no lo usas
PLAYER_CLIENTS = ["mweb", "tv", "web", "android"]

SAFE_CHARS = r"[^A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ()_. -]"

# Candidatos de idioma (prefijos y exactos) para español:
SPANISH_LANG_CANDIDATES = [
    "es-ES",
    "es-419",
    "es",
    "es.*",   # es-AR, es-MX, es-CU, es.automatic, etc.
    "spa",    # poco común, pero a veces aparece
]

# Prioridad para elegir el VTT si hay varios
LANG_PRIORITY = [
    "es-ES",
    "es-419",
    "es",
    # variantes es.* después
]

# Fallback si no hay español: coger el primer idioma disponible de automatic_captions
FALLBACK_TO_ANY_AUTO = True

# Si hay que caer a un auto-captions no español, prioriza en este orden
FALLBACK_AUTO_PRIORITY = ["es-ES", "es-419", "es", "pt", "en"]

# =======================
# UTILIDADES GENERALES
# =======================
WS_RE   = re.compile(r"\s+")
_TS_RE  = re.compile(r"-->\s")         # líneas de tiempo
_NUM_RE = re.compile(r"^\d+$")         # numeración de cues
_TAG_RE = re.compile(r"<[^>]+>")       # etiquetas HTML/Style

IGNORE_PREFIXES = (
    "WEBVTT", "NOTE", "X-TIMESTAMP-MAP", "Kind:", "Language:",
    "STYLE", "REGION", "##", "align:", "position:", "line:", "size:"
)

NOISE_TOKENS = ("♪", "♫")


def safe_filename(name: str) -> str:
    name = name.strip().replace("/", "-").replace("\\", "-")
    name = re.sub(SAFE_CHARS, "", name)
    name = re.sub(r"\s+", " ", name)
    return name[:200] if len(name) > 200 else name


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_videos_from_playlists_folder(folder: Path):
    """
    Recorre todos los JSON de 'folder' y genera:
      (playlist_title, playlist_safe, playlist_url, video_title, video_url, video_id)
    """
    if not folder.is_dir():
        raise FileNotFoundError(f"La carpeta de playlists '{folder}' no existe.")

    for json_file in sorted(folder.glob("*.json")):
        try:
            data = load_json(json_file)
        except Exception as e:
            print(f"WARNING: no se pudo leer {json_file.name}: {e}", file=sys.stderr)
            continue

        playlist_title = data.get("title") or json_file.stem
        playlist_id = data.get("id", "")
        playlist_url = data.get("url", "")
        playlist_safe = safe_filename(playlist_title or playlist_id or json_file.stem)

        items = data.get("items") or []
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("type") and it.get("type") != "video":
                continue
            title = it.get("title") or f"video_{it.get('id', '')}"
            url = it.get("url") or (f"https://www.youtube.com/watch?v={it.get('id')}" if it.get("id") else "")
            vid = it.get("id") or ""
            if url and vid and title and "[Deleted video]" not in title:
                yield playlist_title, playlist_safe, playlist_url, title, url, vid


def normalize_line(s: str) -> str:
    s = _TAG_RE.sub("", s)
    for tok in NOISE_TOKENS:
        s = s.replace(tok, "")
    s = s.strip()
    s = WS_RE.sub(" ", s)
    return s


def vtt_to_solid_text(vtt_path: Path) -> str:
    if not vtt_path.exists():
        return ""
    lines_clean: List[str] = []
    last_seen = deque(maxlen=3)
    with vtt_path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            s = raw.strip()
            if not s:
                continue
            if s.startswith(IGNORE_PREFIXES):
                continue
            if _NUM_RE.fullmatch(s):
                continue
            if _TS_RE.search(s):
                continue
            s = normalize_line(s)
            if not s:
                continue
            if s in last_seen:
                continue
            lines_clean.append(s)
            last_seen.append(s)
    if not lines_clean:
        return ""
    text = " ".join(lines_clean)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(WS_RE, " ", text).strip()
    return text

# =======================
# YT-DLP HELPERS
# =======================
def _build_common_cmd(url: str, base_out: Path) -> List[str]:
    cmd = [
        "yt-dlp",
        "--user-agent", USER_AGENT,
        "--skip-download",
        "--sub-format", "vtt/srv3",
        "--convert-subs", "vtt",
        "--output", str(base_out) + ".%(ext)s",
        url,
    ]
    if COOKIES_FILE.exists():
        cmd = ["yt-dlp", "--cookies", str(COOKIES_FILE)] + cmd[1:]
    return cmd


def _list_subs(url: str, player_client: str) -> str:
    """Devuelve el texto de --list-subs para logging."""
    cmd = _build_common_cmd(url, Path("dummy"))
    cmd += ["--list-subs", "--extractor-args", f"youtube:player_client={player_client}"]
    try:
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.stdout.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.stdout.decode("utf-8", errors="ignore") if e.stdout else str(e)


def _spanish_glob_candidates(base_out: Path) -> List[Path]:
    # Cualquier archivo que empiece por el nombre base y tenga .es*.vtt
    pattern = base_out.name + ".es*.vtt"
    return sorted(base_out.parent.glob(pattern))


def _lang_from_filename(path: Path, base_stem: str) -> str:
    # "<base>.<lang>.vtt" -> extrae <lang>
    name = path.name
    if name.startswith(base_stem + "."):
        rest = name[len(base_stem) + 1 :]
    else:
        rest = name
    if rest.lower().endswith(".vtt"):
        rest = rest[:-4]
    return rest


def _pick_best_spanish_vtt(base_out: Path) -> Optional[Tuple[Path, str]]:
    """Elige el mejor VTT español disponible y devuelve (ruta, lang_code)."""
    candidates = _spanish_glob_candidates(base_out)
    if not candidates:
        return None

    def score(p: Path) -> Tuple[int, str]:
        lang = _lang_from_filename(p, base_out.name)
        for idx, tag in enumerate(LANG_PRIORITY):
            if lang == tag:
                return (idx, lang)
        if lang.startswith("es.") or lang.startswith("es-"):
            return (len(LANG_PRIORITY), lang)
        if lang == "es":
            return (2, lang)
        return (999, lang)

    ranked = sorted(((score(p), p) for p in candidates), key=lambda x: x[0])
    best = ranked[0][1]
    best_lang = _lang_from_filename(best, base_out.name)
    return best, best_lang

# =======================
# DESCARGA PRINCIPAL (con fallback)
# =======================
def download_spanish_with_ytdlp(url: str, base_out: Path) -> Optional[Tuple[Path, str, str]]:
    """
    1) Sonda -J para ver claves reales (subtitles + automatic_captions) y pide EXACTAMENTE las españolas.
    2) Si no hay español y FALLBACK_TO_ANY_AUTO=True: baja el primer auto-captions disponible
       (prioriza FALLBACK_AUTO_PRIORITY).
    3) Si aun así no hay nada usable, intenta rescate con --all-subs y filtra.
    Devuelve (ruta_vtt, lang_code, player_client) o None.
    """
    def probe_json(client: str) -> dict:
        cmd = [
            "yt-dlp",
            "--user-agent", USER_AGENT,
            "-J", url,
            "--extractor-args", f"youtube:player_client={client}",
        ]
        if COOKIES_FILE.exists():
            cmd = ["yt-dlp", "--cookies", str(COOKIES_FILE)] + cmd[1:]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            return {}
        try:
            return json.loads(p.stdout.decode("utf-8", "ignore"))
        except Exception:
            return {}

    def pick_spanish_keys(info: dict) -> List[str]:
        keys = set()
        for field in ("subtitles", "automatic_captions"):
            d = info.get(field) or {}
            for lang in d.keys():
                if lang == "es" or lang.startswith("es-") or lang.startswith("es.") or lang == "spa":
                    keys.add(lang)
        ordered = ["es-ES", "es-419", "es", *sorted([k for k in keys if k not in {"es-ES","es-419","es"}])]
        return [k for k in ordered if k in keys]

    def pick_fallback_auto_key(info: dict) -> Optional[str]:
        auto = info.get("automatic_captions") or {}
        if not auto:
            return None
        # 1) prioridad preferida
        for pref in FALLBACK_AUTO_PRIORITY:
            for lang in auto.keys():
                if lang == pref or lang.startswith(pref + ".") or (pref == "es" and (lang.startswith("es-") or lang.startswith("es."))):
                    return lang
        # 2) si no, la primera clave disponible
        for lang in auto.keys():
            return lang
        return None

    def run_download_with_langs(langs: List[str], client: str) -> Optional[Tuple[Path, str, str]]:
        cmd = [
            "yt-dlp",
            "--user-agent", USER_AGENT,
            "--skip-download",
            "--write-subs", "--write-auto-subs",
            "--sub-format", "vtt/srv3",
            "--convert-subs", "vtt",
            "--sub-langs", ",".join(langs),
            "--output", str(base_out) + ".%(ext)s",
            "--extractor-args", f"youtube:player_client={client}",
            url,
        ]
        if COOKIES_FILE.exists():
            cmd = ["yt-dlp", "--cookies", str(COOKIES_FILE)] + cmd[1:]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pick = _pick_best_spanish_vtt(base_out)
            if pick:
                vtt_path, lang_code = pick
                return (vtt_path, lang_code, client)
            # Si no hay .es*.vtt, quizá el idioma fue otro (fallback): busca cualquier .<lang>.vtt solicitado
            for lang in langs:
                maybe = base_out.with_name(base_out.name + f".{lang}.vtt")
                if maybe.exists():
                    return (maybe, lang, client)
        except subprocess.CalledProcessError:
            pass
        return None

    def all_subs_rescue(client: str) -> Optional[Tuple[Path, str, str]]:
        cmd = [
            "yt-dlp",
            "--user-agent", USER_AGENT,
            "--skip-download",
            "--all-subs",
            "--sub-format", "vtt/srv3",
            "--convert-subs", "vtt",
            "--output", str(base_out) + ".%(ext)s",
            "--extractor-args", f"youtube:player_client={client}",
            url,
        ]
        if COOKIES_FILE.exists():
            cmd = ["yt-dlp", "--cookies", str(COOKIES_FILE)] + cmd[1:]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # 1º intenta español
            pick = _pick_best_spanish_vtt(base_out)
            if pick:
                vtt_path, lang_code = pick
                return (vtt_path, lang_code, client)
            # 2º si no hay español, cualquier vtt priorizado
            vtts = sorted(base_out.parent.glob(base_out.name + ".*.vtt"))
            langs_to_paths = {p.name[len(base_out.name)+1:-4]: p for p in vtts}
            for pref in FALLBACK_AUTO_PRIORITY:
                for lang, path in langs_to_paths.items():
                    if lang == pref or lang.startswith(pref + ".") or (pref == "es" and (lang.startswith("es-") or lang.startswith("es."))):
                        return (path, lang, client)
            if vtts:
                p = vtts[0]
                lang = p.name[len(base_out.name)+1:-4]
                return (p, lang, client)
        except subprocess.CalledProcessError:
            pass
        return None

    # === Flujo principal por clientes ===
    for client in PLAYER_CLIENTS:
        info = probe_json(client)
        # 1) Idiomas españoles exactos
        es_langs = pick_spanish_keys(info)
        if es_langs:
            got = run_download_with_langs(es_langs, client)
            if got:
                return got

        # 2) Fallback: primer auto disponible (p.ej. 'en'), si está activado
        if FALLBACK_TO_ANY_AUTO:
            fb = pick_fallback_auto_key(info)
            if fb:
                got = run_download_with_langs([fb], client)
                if got:
                    return got

        # 3) Rescate --all-subs y luego elegir
        got = all_subs_rescue(client)
        if got:
            return got

    # Segundo intento de rescate global si nada funcionó
    for client in PLAYER_CLIENTS:
        got = all_subs_rescue(client)
        if got:
            return got

    return None

# =======================
# MAIN
# =======================
def main():
    if not PLAYLISTS_DIR.is_dir():
        print(f"ERROR: la carpeta '{PLAYLISTS_DIR}' no existe. Ejecuta antes el script de expansión.", file=sys.stderr)
        sys.exit(1)

    OUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    ok = 0
    skipped = 0
    failed = 0

    for playlist_title, playlist_safe, playlist_url, title, url, vid in iter_videos_from_playlists_folder(PLAYLISTS_DIR):
        total += 1

        playlist_dir = OUT_BASE_DIR / playlist_safe
        playlist_dir.mkdir(parents=True, exist_ok=True)

        base_name = safe_filename(title)
        base_out = playlist_dir / base_name     # sin extensión
        txt_path = playlist_dir / f"{base_name}.txt"
        log_path = playlist_dir / f"{base_name}.log"

        if txt_path.exists():
            print(f"[SKIP] ({playlist_title}) Ya existe: {txt_path.name}")
            continue

        print(f"[{total:03d}] [{playlist_title}] {title} -> {url}")

        # 1) Descargar subtítulos (español o fallback)
        pick = download_spanish_with_ytdlp(url, base_out)

        if not pick:
            skipped += 1
            # Para diagnóstico: listar subs disponibles por cada client
            lists = []
            for client in PLAYER_CLIENTS:
                ls = _list_subs(url, client)
                lists.append(f"\n--- --list-subs (client={client}) ---\n{ls}")
            log_path.write_text(
                f"No se pudieron obtener subtítulos.\n"
                f"PLAYLIST:{playlist_title}\nPLAYLIST_URL:{playlist_url}\n"
                f"TITLE:{title}\nURL:{url}\nID:{vid}\n"
                f"Intentos: español -> fallback_any_auto -> all-subs\n"
                f"{''.join(lists)}\n",
                encoding="utf-8"
            )
            print("  · No hay subtítulos utilizables (registrado .log)")
            time.sleep(SLEEP_BETWEEN)
            continue

        vtt_path, lang_code, client_used = pick

        # 2) Convertir VTT -> TEXTO SÓLIDO
        try:
            solid = vtt_to_solid_text(vtt_path)
            if not solid:
                failed += 1
                log_path.write_text(
                    f"VTT vacío o no legible tras limpieza.\n"
                    f"PLAYLIST:{playlist_title}\nPLAYLIST_URL:{playlist_url}\n"
                    f"TITLE:{title}\nURL:{url}\nID:{vid}\n"
                    f"VTT: {vtt_path.name} ({lang_code}) client={client_used}\n",
                    encoding="utf-8"
                )
                print("  ✗ VTT vacío/ilegible (registrado .log)")
            else:
                fallback_mark = ""
                if lang_code not in ("es", "es-ES", "es-419") and not lang_code.startswith("es-") and not lang_code.startswith("es."):
                    fallback_mark = " (fallback_any_auto)"
                header = [
                    f"PLAYLIST: {playlist_title}",
                    f"PLAYLIST_URL: {playlist_url}",
                    f"TITLE: {title}",
                    f"URL:   {url}",
                    f"ID:    {vid}",
                    f"SOURCE: yt-dlp [{lang_code}] client={client_used}{fallback_mark}",
                    "-" * 60,
                    ""
                ]
                txt_path.write_text("\n".join(header) + solid, encoding="utf-8")
                ok += 1
                print(f"  ✓ Transcripción guardada (texto sólido): {txt_path.name}")
        except Exception as e:
            failed += 1
            log_path.write_text(
                f"Error al convertir VTT->TXT: {e}\n"
                f"PLAYLIST:{playlist_title}\nPLAYLIST_URL:{playlist_url}\n"
                f"TITLE:{title}\nURL:{url}\nID:{vid}\n"
                f"VTT: {vtt_path.name} ({lang_code}) client={client_used}\n",
                encoding="utf-8"
            )
            print("  ✗ Error VTT->TXT (registrado .log)")

        time.sleep(SLEEP_BETWEEN)

    print("\n=== RESUMEN ===")
    print(f"Vídeos totales:   {total}")
    print(f"OK (transcritos): {ok}")
    print(f"Omitidos:         {skipped}  (sin subtítulos utilizables)")
    print(f"Fallidos:         {failed}")


if __name__ == "__main__":
    main()
