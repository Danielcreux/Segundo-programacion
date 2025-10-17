# cabeceras.py
import os
from typing import Iterable, Optional, List, Set, Dict

# ==== Opcional: documentación con IA (Ollama/Qwen) ====
try:
    from docai import document_code_with_ollama  # docai.py debe estar en el mismo directorio o en PYTHONPATH
    _DOC_AI_AVAILABLE = True
except Exception:
    _DOC_AI_AVAILABLE = False

# --- helper de listado (mismo criterio que arbol.py) ---
def list_entries(path: str, show_hidden: bool = False) -> Iterable[os.DirEntry]:
    with os.scandir(path) as it:
        entries = [e for e in it if show_hidden or not e.name.startswith(".")]
    # Directorios primero, luego ficheros; orden case-insensitive
    entries.sort(key=lambda e: (e.is_file(), e.name.casefold()))
    return entries

def _md_escape(text: str) -> str:
    """Escape mínimo para Markdown en títulos/enlaces."""
    for ch in ["[", "]", "(", ")", "#", "*", "_", "`"]:
        text = text.replace(ch, f"\\{ch}")
    return text

def _rel_link(from_dir: str, target_path: str) -> str:
    """Enlace relativo (más portable en repos)."""
    try:
        return os.path.relpath(target_path, start=from_dir)
    except ValueError:
        return os.path.basename(target_path)

def _infer_lang_from_ext(ext: str, mapping: Optional[Dict[str, str]] = None) -> str:
    default_map = {
        "py":"python","js":"javascript","ts":"typescript","tsx":"tsx","jsx":"jsx","json":"json",
        "yml":"yaml","yaml":"yaml","md":"markdown","html":"html","htm":"html","css":"css","php":"php",
        "sql":"sql","sh":"bash","bash":"bash","ini":"","cfg":"","txt":"","xml":"xml","csv":"","toml":"toml",
        "rs":"rust","go":"go","java":"java","kt":"kotlin","c":"c","h":"c","cpp":"cpp","hpp":"cpp",
        "cs":"csharp","rb":"ruby","lua":"lua","r":"r","pl":"perl","swift":"swift","makefile":"make",
        "dockerfile":"dockerfile","env":""
    }
    mp = {**default_map, **(mapping or {})}
    return mp.get(ext.lower(), "")

# --- filtros binario/texto para no volcar basura ---
_KNOWN_BINARY_EXT = {
    "pyc","pyo","so","o","a","bin","exe","dll","dylib","class","jar","zip","7z","gz","bz2",
    "xz","png","jpg","jpeg","gif","webp","ico","pdf","mp3","wav","ogg","mp4","mov","avi","mkv","ttf","otf","woff","woff2"
}

def _looks_text_bytes(sample: bytes, min_printable_ratio: float = 0.85) -> bool:
    if b"\x00" in sample:  # null byte => binario
        return False
    printable = sum(ch >= 9 and (ch == 9 or ch == 10 or ch == 13 or 32 <= ch <= 126) for ch in sample)
    ratio = printable / max(1, len(sample))
    return ratio >= min_printable_ratio

def _is_text_file(path: str, peek: int = 4096) -> bool:
    try:
        with open(path, "rb") as fh:
            sample = fh.read(peek)
        return _looks_text_bytes(sample)
    except Exception:
        return False

def _read_text_file_safely(path: str, max_bytes: Optional[int] = 262_144) -> str:
    """
    Lectura robusta con tope de tamaño y decodificación tolerante.
    Intenta utf-8, utf-8-sig, cp1252, latin-1; última opción utf-8 con replacement.
    """
    try:
        if max_bytes is not None and os.path.getsize(path) > max_bytes:
            return f"[Contenido omitido: archivo mayor de {max_bytes} bytes]"
        with open(path, "rb") as fh:
            data = fh.read(None if max_bytes is None else max_bytes)
        for enc in ("utf-8","utf-8-sig","cp1252","latin-1"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[No se pudo leer el archivo: {e}]"

def _fenced_block(content: str, lang: str = "", escape_html_in_fences: bool = False) -> List[str]:
    """
    Devuelve un bloque de código con fences. Si hay ``` en el contenido, usa ~~~.
    Con escape_html_in_fences=True, escapa < > & para que jamás renderice HTML.
    """
    if escape_html_in_fences:
        content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if "```" in content:
        start = f"~~~{lang}" if lang else "~~~"
        end = "~~~"
        return [start, content, end]
    else:
        start = f"```{lang}" if lang else "```"
        end = "```"
        return [start, content, end]

def draw_markdown(
    path: str,
    show_hidden: bool = False,
    max_depth: Optional[int] = None,
    base_level: int = 1,
    files_as_headings: bool = False,
    link_files: bool = True,
    allowed_extensions: Optional[Set[str]] = None,   # p.ej. {"py","js","md","html","css"}
    max_file_bytes: Optional[int] = 262_144,
    lang_override: Optional[Dict[str, str]] = None,
    use_emojis: bool = True,
    escape_html_for_exts: Set[str] = frozenset({"html","htm","xml","xhtml","svg"}),
    use_ai_doc: bool = True,                # activa/desactiva documentación IA
    ai_only_when_allowed_ext: bool = True,  # si True, solo pasa a IA extensiones permitidas
    _current_depth: int = 0,
    _root_dir: Optional[str] = None,
) -> List[str]:
    """
    Índice Markdown de la carpeta `path` con contenido inline de archivos (code fences)
    y, si está disponible docai.py, documentación automática ANTES de cada bloque de código.
    """
    lines: List[str] = []
    if _root_dir is None:
        _root_dir = os.path.abspath(path)

    if allowed_extensions is not None:
        allowed_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}

    # Encabezado de carpeta
    level = min(max(1, base_level + _current_depth), 6)
    name = os.path.basename(os.path.normpath(path)) or path
    folder_icon = "📁 " if use_emojis else ""
    lines.append(f'{"#" * level} {folder_icon}{_md_escape(name)}')

    # Límite de profundidad
    if max_depth is not None and _current_depth >= max_depth:
        return lines

    # Listado
    try:
        entries = list_entries(path, show_hidden=show_hidden)
    except PermissionError:
        lines.append("> ⛔ Permiso denegado")
        return lines
    except FileNotFoundError:
        lines.append("> ⚠️  Carpeta no encontrada")
        return lines

    dirs  = [e for e in entries if e.is_dir(follow_symlinks=False)]
    files = [e for e in entries if e.is_file(follow_symlinks=False)]
    others= [e for e in entries if not e.is_dir(follow_symlinks=False) and not e.is_file(follow_symlinks=False)]

    file_icon = "📄 " if use_emojis else ""
    link_icon = "🔗 " if use_emojis else ""

    def _should_include_content(file_entry: os.DirEntry, ext: str) -> bool:
        # extensiones permitidas (si se especifican)
        if allowed_extensions is not None and ext not in allowed_extensions:
            return False
        # bloquear binarios conocidos
        if ext in _KNOWN_BINARY_EXT:
            return False
        # debe parecer texto
        if not _is_text_file(file_entry.path):
            return False
        return True

    def _ai_doc_for(filename: str, content: str, ext: str) -> List[str]:
        """
        Genera documentación IA en Markdown (sin fences). Devuelve lista de líneas.
        """
        if not use_ai_doc or not _DOC_AI_AVAILABLE:
            return []
        if ai_only_when_allowed_ext and allowed_extensions is not None and ext not in allowed_extensions:
            return []
        try:
            md = document_code_with_ollama(filename=filename, code=content, ext=ext)
            return md.splitlines()
        except Exception as e:
            return [f"> ⚠️ No se pudo generar documentación automática para {filename}: {e}"]

    # === Ficheros ===
    if files_as_headings:
        # Cada fichero como sub-encabezado, luego (opcional) doc IA + código
        for f in files:
            file_level = min(level + 1, 6)
            display_text = f"{file_icon}{_md_escape(f.name)}"
            rel = _rel_link(_root_dir, f.path) if link_files else None
            display = f"[{display_text}]({_md_escape(rel)})" if rel else display_text
            lines.append(f'{"#" * file_level} {display}')

            ext = os.path.splitext(f.name)[1].lstrip(".").lower()
            if _should_include_content(f, ext):
                lang = _infer_lang_from_ext(ext, lang_override)
                content = _read_text_file_safely(f.path, max_file_bytes)
                escape_html = ext in escape_html_for_exts

                # 1) Doc IA antes del bloque de código
                ai_lines = _ai_doc_for(f.name, content, ext)
                if ai_lines:
                    lines.append("")  # separación
                    lines.extend(ai_lines)

                # 2) Bloque de código
                lines.append("")
                lines.extend(_fenced_block(content, lang, escape_html_in_fences=escape_html))
    else:
        # Lista con bullets; mantener buen Markdown (línea en blanco + 4 espacios para bloques)
        if files or others:
            lines.append("")
        for f in files:
            title = _md_escape(f.name)
            rel = _rel_link(_root_dir, f.path) if link_files else None
            label = f"[{title}]({_md_escape(rel)})" if rel else title
            lines.append(f"- {file_icon}{label}")

            ext = os.path.splitext(f.name)[1].lstrip(".").lower()
            if _should_include_content(f, ext):
                lang = _infer_lang_from_ext(ext, lang_override)
                content = _read_text_file_safely(f.path, max_file_bytes)
                escape_html = ext in escape_html_for_exts

                # 1) Doc IA (indentada bajo el bullet)
                ai_lines = _ai_doc_for(f.name, content, ext)
                if ai_lines:
                    lines.append("")  # línea en blanco
                    for ln in ai_lines:
                        lines.append("    " + ln if ln else "    ")

                # 2) Bloque de código (también indentado)
                lines.append("")
                for ln in _fenced_block(content, lang, escape_html_in_fences=escape_html):
                    lines.append("    " + ln if ln else "    ")

        for o in others:
            lines.append(f"- {link_icon}{_md_escape(o.name)}")

    # === Subdirectorios ===
    for d in dirs:
        lines.extend(
            draw_markdown(
                d.path,
                show_hidden=show_hidden,
                max_depth=max_depth,
                base_level=base_level,
                files_as_headings=files_as_headings,
                link_files=link_files,
                allowed_extensions=allowed_extensions,
                max_file_bytes=max_file_bytes,
                lang_override=lang_override,
                use_emojis=use_emojis,
                escape_html_for_exts=escape_html_for_exts,
                use_ai_doc=use_ai_doc,
                ai_only_when_allowed_ext=ai_only_when_allowed_ext,
                _current_depth=_current_depth + 1,
                _root_dir=_root_dir,
            )
        )

    return lines

# === Ejecución directa de ejemplo ===
if __name__ == "__main__":
    root = "."
    md_lines = draw_markdown(
        root,
        show_hidden=False,
        max_depth=None,
        base_level=1,
        files_as_headings=False,           # True: ficheros como headings
        link_files=True,
        allowed_extensions={"js","py","md","html","css","php"},  # solo estas extensiones llevan contenido
        max_file_bytes=200_000,
        lang_override=None,
        use_emojis=True,                   # si ves mojibake, pon False
        escape_html_for_exts={"html","htm","xml","xhtml","svg"},
        use_ai_doc=True,                   # genera documentación con IA (requiere docai.py + Ollama)
        ai_only_when_allowed_ext=True,
    )
    print("\n".join(md_lines))
