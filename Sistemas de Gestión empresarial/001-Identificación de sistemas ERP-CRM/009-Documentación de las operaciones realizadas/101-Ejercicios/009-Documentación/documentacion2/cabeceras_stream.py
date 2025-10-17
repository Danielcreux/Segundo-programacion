# cabeceras_stream.py
# Stream Markdown index to disk as it's generated, and ask Ollama/Qwen
# to document each file with awareness of the whole project's structure.

import os
from typing import Iterable, Optional, Set, Dict, TextIO, List

# ==== Fragmentos inteligentes ====
try:
    from fragmentos_inteligentes import extraer_fragmentos_clave
    _FRAGMENTOS_AVAILABLE = True
except ImportError:
    _FRAGMENTOS_AVAILABLE = False

# ==== Optional: AI documentation (Ollama/Qwen) ====
try:
    from docai import (
        document_code_with_project as _doc_ai_with_project,
        build_project_context as _build_project_context_external,
    )
    _DOC_AI_WITH_PROJECT = True
    _DOC_AI_AVAILABLE = True
except Exception:
    _DOC_AI_WITH_PROJECT = False
    try:
        from docai import document_code_with_ollama as _doc_ai_simple
        _DOC_AI_AVAILABLE = True
    except Exception:
        _DOC_AI_AVAILABLE = False
        _doc_ai_simple = None

# ---------- helpers ----------
def list_entries(path: str, show_hidden: bool = False) -> Iterable[os.DirEntry]:
    with os.scandir(path) as it:
        entries = [e for e in it if show_hidden or not e.name.startswith(".")]
    # directories first, then files; case-insensitive
    entries.sort(key=lambda e: (e.is_file(), e.name.casefold()))
    return entries

def _md_escape(text: str) -> str:
    for ch in ["[", "]", "(", ")", "#", "*", "_", "`"]:
        text = text.replace(ch, f"\\{ch}")
    return text

def _rel_link(from_dir: str, target_path: str) -> str:
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
    return mp.get((ext or "").lower(), "")

_KNOWN_BINARY_EXT = {
    "pyc","pyo","so","o","a","bin","exe","dll","dylib","class","jar","zip","7z","gz","bz2",
    "xz","png","jpg","jpeg","gif","webp","ico","pdf","mp3","wav","ogg","mp4","mov","avi","mkv",
    "ttf","otf","woff","woff2"
}

def _looks_text_bytes(sample: bytes, min_printable_ratio: float = 0.85) -> bool:
    if b"\x00" in sample:
        return False
    printable = sum(ch >= 9 and (ch in (9, 10, 13) or 32 <= ch <= 126) for ch in sample)
    return printable / max(1, len(sample)) >= min_printable_ratio

def _is_text_file(path: str, peek: int = 4096) -> bool:
    try:
        with open(path, "rb") as fh:
            sample = fh.read(peek)
        return _looks_text_bytes(sample)
    except Exception:
        return False

def _read_text_file_safely(path: str, max_bytes: Optional[int] = 262_144) -> str:
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
    if escape_html_in_fences:
        content = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    if "```" in content:
        return [f"~~~{lang}" if lang else "~~~", content, "~~~"]
    return [f"```{lang}" if lang else "```", content, "```"]

def _formatear_contenido_con_fragmentos(contenido: str, lenguaje: str, filename: str, max_lineas_preview: int = 30) -> List[str]:
    """
    En lugar de mostrar todo el código, muestra fragmentos clave con explicaciones
    """
    lineas = []
    
    if not _FRAGMENTOS_AVAILABLE or len(contenido.strip()) < 100:
        # Si no hay fragmentos disponibles o el archivo es muy pequeño, mostrar preview
        lineas_contenido = contenido.split('\n')
        if len(lineas_contenido) <= max_lineas_preview:
            preview = contenido
        else:
            preview = '\n'.join(lineas_contenido[:max_lineas_preview])
            preview += f"\n\n// ... [{len(lineas_contenido) - max_lineas_preview} líneas más]"
        return _fenced_block(preview, lenguaje)
    
    try:
        fragmentos = extraer_fragmentos_clave(contenido, lenguaje, max_fragmentos=4)
        
        if not fragmentos:
            # Si no se pudieron extraer fragmentos, mostrar preview
            lineas_contenido = contenido.split('\n')
            preview = '\n'.join(lineas_contenido[:max_lineas_preview])
            if len(lineas_contenido) > max_lineas_preview:
                preview += f"\n\n// ... [{len(lineas_contenido) - max_lineas_preview} líneas más]"
            return _fenced_block(preview, lenguaje)
        
        # Mostrar fragmentos organizados
        lineas.append("**🔍 Fragmentos clave del código:**")
        lineas.append("")
        
        for i, fragmento in enumerate(fragmentos, 1):
            lineas.append(f"**{i}. {fragmento['descripcion']}**")
            if 'linea_inicio' in fragmento:
                linea_fin = fragmento.get('linea_fin', fragmento['linea_inicio'])
                lineas.append(f"*Líneas {fragmento['linea_inicio']}-{linea_fin}*")
            lineas.append("")
            lineas.extend(_fenced_block(fragmento['codigo'], lenguaje))
            lineas.append("")
        
        # Información del archivo completo
        total_lineas = len(contenido.split('\n'))
        lineas.append("---")
        lineas.append(f"**📄 Archivo completo:** `{filename}` ({total_lineas} líneas)")
        lineas.append("*Para ver el código completo, abre el archivo directamente*")
        
    except Exception as e:
        # Fallback: mostrar contenido preview
        print(f"Error al extraer fragmentos: {e}")
        lineas_contenido = contenido.split('\n')
        preview = '\n'.join(lineas_contenido[:max_lineas_preview])
        if len(lineas_contenido) > max_lineas_preview:
            preview += f"\n\n// ... [{len(lineas_contenido) - max_lineas_preview} líneas más]"
        return _fenced_block(preview, lenguaje)
    
    return lineas

# ---------- local project-context builder (fallback) ----------
def _build_project_context_local(
    root: str,
    allowed_exts: Optional[Set[str]] = None,
    max_file_bytes: int = 50_000,
    max_files: Optional[int] = None,
) -> str:
    """
    Build a compact Markdown snapshot of the project: folder headings + capped file contents.
    """
    lines: List[str] = []
    count = 0
    root_abs = os.path.abspath(root)
    for dirpath, _, files in os.walk(root_abs):
        rel = os.path.relpath(dirpath, root_abs)
        lines.append(f"\n## 📁 {rel if rel != '.' else os.path.basename(root_abs)}")
        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lstrip(".").lower()
            if allowed_exts and ext not in allowed_exts:
                continue
            if ext in _KNOWN_BINARY_EXT:
                continue
            path = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(path)
                with open(path, "rb") as fh:
                    raw = fh.read(min(size, max_file_bytes))
                if not _looks_text_bytes(raw):
                    continue
                content = raw.decode("utf-8", errors="replace")
                lines.append(f"\n### 📄 {fname}")
                lines.append("```" + (ext or ""))
                lines.append(content)
                if size > max_file_bytes:
                    lines.append(f"... [truncated after {max_file_bytes} bytes]")
                lines.append("```")
                count += 1
                if max_files is not None and count >= max_files:
                    lines.append("\n> [Contexto truncado: límite de archivos alcanzado]")
                    return "\n".join(lines)
            except Exception as e:
                lines.append(f"\n### 📄 {fname} (no leído: {e})")
    return "\n".join(lines)

# ---------- streaming core ----------
def write_line(out: TextIO, line: str = "") -> None:
    out.write(line + "\n")
    out.flush()

def _ai_doc_lines(filename: str, content: str, ext: str) -> List[str]:
    if not _DOC_AI_AVAILABLE:
        return []
    try:
        if _DOC_AI_WITH_PROJECT:
            md = _doc_ai_with_project(filename=filename, code=content, ext=ext, project_context="")
            return md.strip().splitlines() if md.strip() else []
        elif _doc_ai_simple is not None:
            # LLAMADA CORREGIDA - pasa los 3 parámetros requeridos
            md = _doc_ai_simple(filename, content, ext)
            if md and md.strip():
                return md.strip().splitlines()
            else:
                return []
        else:
            return []
    except Exception as e:
        return [f"> ⚠️ Error en documentación IA: {e}"]

def write_markdown_stream(
    out: TextIO,
    path: str,
    *,
    show_hidden: bool = False,
    max_depth: Optional[int] = None,
    base_level: int = 1,
    files_as_headings: bool = False,
    link_files: bool = True,
    allowed_extensions: Optional[Set[str]] = None,
    max_file_bytes: Optional[int] = 262_144,
    lang_override: Optional[Dict[str, str]] = None,
    use_emojis: bool = True,
    escape_html_for_exts: Set[str] = frozenset({"html","htm","xml","xhtml","svg"}),
    use_ai_doc: bool = True,
    ai_only_when_allowed_ext: bool = True,
    project_context: Optional[str] = None,
    project_ctx_allowed_exts: Optional[Set[str]] = None,
    project_ctx_max_file_bytes: int = 50_000,
    project_ctx_max_chars: Optional[int] = 400_000,
    _current_depth: int = 0,
    _root_dir: Optional[str] = None,
) -> None:
    """
    Stream the Markdown for `path` directly to `out`, flushing as we go.
    """
    # Build/context once at the top-level if needed
    if _root_dir is None:
        _root_dir = os.path.abspath(path)
    if use_ai_doc and _DOC_AI_AVAILABLE and project_context is None and _current_depth == 0:
        ctx_exts = project_ctx_allowed_exts or (allowed_extensions or {"py","js","ts","tsx","jsx","html","css","md","php","json","yaml","yml","xml","sql","sh"})
        if _DOC_AI_WITH_PROJECT and _build_project_context_external is not None:
            try:
                project_context = _build_project_context_external(
                    _root_dir,
                    allowed_exts=ctx_exts,
                    max_file_bytes=project_ctx_max_file_bytes,
                )
            except Exception:
                project_context = _build_project_context_local(
                    _root_dir,
                    allowed_exts=ctx_exts,
                    max_file_bytes=project_ctx_max_file_bytes,
                )
        else:
            project_context = _build_project_context_local(
                _root_dir,
                allowed_exts=ctx_exts,
                max_file_bytes=project_ctx_max_file_bytes,
            )
        if project_ctx_max_chars is not None and len(project_context) > project_ctx_max_chars:
            project_context = project_context[:project_ctx_max_chars] + "\n\n> [Contexto truncado por longitud]\n"

    # normalize allowed file-content exts
    if allowed_extensions is not None:
        allowed_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}

    # folder heading
    level = min(max(1, base_level + _current_depth), 6)
    name = os.path.basename(os.path.normpath(path)) or path
    folder_icon = "📁 " if use_emojis else ""
    write_line(out, f'{"#" * level} {folder_icon}{_md_escape(name)}')

    # depth stop
    if max_depth is not None and _current_depth >= max_depth:
        return

    # list entries
    try:
        entries = list_entries(path, show_hidden=show_hidden)
    except PermissionError:
        write_line(out, "> ⛔ Permiso denegado")
        return
    except FileNotFoundError:
        write_line(out, "> ⚠️  Carpeta no encontrada")
        return

    dirs  = [e for e in entries if e.is_dir(follow_symlinks=False)]
    files = [e for e in entries if e.is_file(follow_symlinks=False)]
    others= [e for e in entries if not e.is_dir(follow_symlinks=False) and not e.is_file(follow_symlinks=False)]

    file_icon = "📄 " if use_emojis else ""
    link_icon = "🔗 " if use_emojis else ""

    def _should_include_content(file_entry: os.DirEntry, ext: str) -> bool:
        if allowed_extensions is not None and ext not in allowed_extensions:
            return False
        if ext in _KNOWN_BINARY_EXT:
            return False
        if not _is_text_file(file_entry.path):
            return False
        return True

    # --- files ---
    if files_as_headings:
        # Each file as its own heading, then AI doc + code
        for f in files:
            file_level = min(level + 1, 6)
            display_text = f"{file_icon}{_md_escape(f.name)}"
            rel = _rel_link(_root_dir, f.path) if link_files else None
            display = f"[{display_text}]({_md_escape(rel)})" if rel else display_text
            write_line(out, f'{"#" * file_level} {display}')

            ext = os.path.splitext(f.name)[1].lstrip(".").lower()
            if _should_include_content(f, ext):
                lang = _infer_lang_from_ext(ext, lang_override)
                content = _read_text_file_safely(f.path, max_file_bytes)
                escape_html = ext in escape_html_for_exts

                # AI doc first
                ai = _ai_doc_lines(f.name, content, ext)
                if ai:
                    write_line(out)
                    for ln in ai: 
                        write_line(out, ln)

                # Code fragments instead of full code
                write_line(out)
                fragment_lines = _formatear_contenido_con_fragmentos(content, lang, f.name)
                for ln in fragment_lines:
                    write_line(out, ln)
                    
    else:
        # Bulleted list; keep Markdown rules
        if files or others:
            write_line(out)
        for f in files:
            title = _md_escape(f.name)
            rel = _rel_link(_root_dir, f.path) if link_files else None
            label = f"[{title}]({_md_escape(rel)})" if rel else title
            write_line(out, f"- {file_icon}{label}")

            ext = os.path.splitext(f.name)[1].lstrip(".").lower()
            if _should_include_content(f, ext):
                lang = _infer_lang_from_ext(ext, lang_override)
                content = _read_text_file_safely(f.path, max_file_bytes)
                escape_html = ext in escape_html_for_exts

                # AI doc
                ai = _ai_doc_lines(f.name, content, ext)
                if ai:
                    write_line(out)
                    for ln in ai:
                        write_line(out, ("    " + ln) if ln else "    ")

                # Code fragments (indented)
                write_line(out)
                fragment_lines = _formatear_contenido_con_fragmentos(content, lang, f.name)
                for ln in fragment_lines:
                    write_line(out, ("    " + ln) if ln else "    ")

        for o in others:
            write_line(out, f"- {link_icon}{_md_escape(o.name)}")

    # --- subdirs (depth-first) ---
    for d in dirs:
        write_markdown_stream(
            out, d.path,
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
            project_context=project_context,
            project_ctx_allowed_exts=project_ctx_allowed_exts,
            project_ctx_max_file_bytes=project_ctx_max_file_bytes,
            project_ctx_max_chars=project_ctx_max_chars,
            _current_depth=_current_depth + 1,
            _root_dir=_root_dir,
        )

# === example direct run ===
if __name__ == "__main__":
    root = "."
    with open("proyecto_documentado.md", "w", encoding="utf-8") as f:
        write_markdown_stream(
            f, root,
            show_hidden=False,
            max_depth=None,
            base_level=1,
            files_as_headings=True,
            link_files=True,
            allowed_extensions={"js","py","md","html","css","php"},
            max_file_bytes=200_000,
            lang_override=None,
            use_emojis=True,
            escape_html_for_exts={"html","htm","xml","xhtml","svg"},
            use_ai_doc=True,
            ai_only_when_allowed_ext=True,
            project_ctx_allowed_exts={"py","js","ts","tsx","jsx","html","css","md","php","json","yaml","yml","xml","sql","sh"},
            project_ctx_max_file_bytes=50_000,
            project_ctx_max_chars=400_000,
        )