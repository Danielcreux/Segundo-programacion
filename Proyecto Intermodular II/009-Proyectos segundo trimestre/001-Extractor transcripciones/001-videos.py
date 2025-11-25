#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Expande una lista de playlists de YouTube (array de URLs) en un JSON por playlist.

Entrada:
  playlists_in.json  ->  [ "https://www.youtube.com/playlist?list=...", ... ]

Salida:
  Carpeta playlists_expandidas/ con un archivo JSON por playlist:

  {
    "id": "<playlist_id>",
    "title": "<playlist_title>",
    "url": "https://www.youtube.com/playlist?list=<playlist_id>",
    "items": [
      { "id": "...", "title": "...", "url": "...", "type": "video" },
      ...
    ]
  }

Requisitos: yt-dlp  (pip install yt-dlp)
"""

import json
import sys
import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("ERROR: yt-dlp is required. Install with: pip install yt-dlp", file=sys.stderr)
    sys.exit(1)

INPUT_FILE = "listas.json"        # JSON con array de URLs de playlists
OUTPUT_DIR = Path("playlists_expandidas")

SAFE_CHARS = r"[^A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ()_. -]"


def safe_filename(name: str) -> str:
    """Sanitiza un texto para usarlo como nombre de archivo."""
    name = name.strip().replace("/", "-").replace("\\", "-")
    name = re.sub(SAFE_CHARS, "", name)
    name = re.sub(r"\s+", " ", name)
    return name[:200] if len(name) > 200 else name


def extract_playlist_id(url):
    """Return playlist ID from any YouTube URL (via 'list=' query param), or None."""
    try:
        qs = parse_qs(urlparse(url).query)
        return qs.get("list", [None])[0]
    except Exception:
        return None


def fetch_playlist_title_and_items(playlist_url):
    """
    Return (title, items) for a playlist URL.
    items = [{id, title, url, type:"video"}, ...]
    """
    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
        "nocheckcertificate": True,
        "noprogress": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    if not info:
        return None, []

    playlist_title = info.get("title")
    entries = []
    if info.get("_type") == "playlist":
        entries = info.get("entries") or []
    else:
        entries = info.get("entries") or []
        if not entries and info.get("id") and info.get("title"):
            entries = [info]
            playlist_title = playlist_title or "Sin título"

    items = []
    for e in entries:
        vid = e.get("id")
        vtitle = e.get("title")
        vurl = f"https://www.youtube.com/watch?v={vid}" if vid else e.get("url")
        if vid and vtitle and vurl:
            items.append({"id": vid, "title": vtitle, "url": vurl, "type": "video"})

    if not playlist_title:
        playlist_title = "Sin título"

    return playlist_title, items


def disambiguate_title(title, existing_titles):
    """Ensure unique title within existing_titles (append ' (2)', ' (3)', ... if needed)."""
    if title not in existing_titles:
        return title
    i = 2
    while True:
        candidate = f"{title} ({i})"
        if candidate not in existing_titles:
            return candidate
        i += 1


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            playlists = json.load(f)
    except Exception as e:
        print(f"ERROR: no se pudo leer '{INPUT_FILE}': {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(playlists, list):
        print(f"ERROR: '{INPUT_FILE}' debe ser un array JSON de URLs de playlists.", file=sys.stderr)
        sys.exit(1)

    used_titles = set()
    total_playlists = 0
    total_videos = 0

    seen_playlist_ids = set()

    for url in playlists:
        if not isinstance(url, str):
            print(f"WARNING: elemento no cadena en JSON, se ignora: {url}", file=sys.stderr)
            continue

        plist = extract_playlist_id(url)
        if not plist:
            print(f"WARNING: URL sin 'list=': {url}", file=sys.stderr)
            continue
        if plist in seen_playlist_ids:
            print(f"INFO: playlist ya procesada, se ignora duplicado: {plist}", file=sys.stderr)
            continue
        seen_playlist_ids.add(plist)

        normalized = f"https://www.youtube.com/playlist?list={plist}"
        print(f"Procesando playlist: {normalized}")

        try:
            ptitle, videos = fetch_playlist_title_and_items(normalized)
        except Exception as e:
            print(f"WARNING: could not fetch playlist {plist}: {e}", file=sys.stderr)
            ptitle, videos = f"Playlist {plist}", []

        unique_title = disambiguate_title(ptitle, used_titles)
        used_titles.add(unique_title)

        safe_title = safe_filename(unique_title)
        out_path = OUTPUT_DIR / f"{safe_title}.json"

        playlist_obj = {
            "id": plist,
            "title": unique_title,
            "url": normalized,
            "items": videos,
        }

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(playlist_obj, f, ensure_ascii=False, indent=2)

        total_playlists += 1
        total_videos += len(videos)
        print(f"  -> Guardado {out_path.name} ({len(videos)} vídeos)")

    print("\nDone.")
    print(f"Playlists procesadas: {total_playlists}")
    print(f"Vídeos totales:       {total_videos}")


if __name__ == "__main__":
    main()
