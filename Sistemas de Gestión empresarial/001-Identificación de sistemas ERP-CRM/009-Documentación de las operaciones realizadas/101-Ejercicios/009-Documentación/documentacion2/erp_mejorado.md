# 📊 ESTRUCTURA DEL PROYECTO

```
..
   ├─ anterior
   │  ├─ cabecera
   │  │  ├─ comportamiento.js
   │  │  ├─ estilo.css
   │  │  └─ index.php
   │  ├─ comun
   │  │  ├─ estilo.css
   │  │  ├─ Ubuntu-B.ttf
   │  │  └─ Ubuntu-R.ttf
   │  ├─ escritorio
   │  │  ├─ comportamiento.js
   │  │  ├─ estilo.css
   │  │  └─ index.html
   │  ├─ iniciarsesion
   │  │  ├─ comportamiento.js
   │  │  ├─ estilo.css
   │  │  └─ index.html
   │  ├─ listadodemodulos
   │  │  ├─ comportamiento.js
   │  │  ├─ estilo.css
   │  │  └─ index.php
   │  ├─ plantillas
   │  │  ├─ calendario
   │  │  ├─ fichas
   │  │  ├─ formulario
   │  │  ├─ grafica
   │  │  ├─ Kanban
   │  │  └─ lista
   │  └─ index.php
   ├─ base de datos
   │  └─ instalacion.sql
   ├─ documentacion
   │  ├─ __pycache__
   │  │  ├─ arbol.cpython-313.pyc
   │  │  ├─ cabeceras_stream.cpython-313.pyc
   │  │  └─ docai.cpython-313.pyc
   │  ├─ arbol.py
   │  ├─ cabeceras.py
   │  ├─ cabeceras_stream.py
   │  ├─ docai.py
   │  ├─ documentacion.py
   │  └─ erp.md
   ├─ documentacion2
   │  ├─ __pycache__
   │  │  ├─ arbol.cpython-313.pyc
   │  │  ├─ cabeceras_stream.cpython-313.pyc
   │  │  └─ docai.cpython-313.pyc
   │  ├─ arbol.py
   │  ├─ cabeceras.py
   │  ├─ cabeceras_stream.py
   │  ├─ docai.py
   │  ├─ documentacion.py
   │  ├─ erp_mejorado.md
   │  └─ ollama_config.py
   ├─ instalador
   │  └─ index.php
   └─ posterior
      ├─ config.php
      ├─ iniciarsesion.php
      └─ listadodemodulos.php
```

---

## ..
### anterior
#### index.php

Este archivo es el archivo principal de un sitio web desarrollado con PHP. Su función principal es proporcionar la estructura básica del sitio, incluyendo la carga de las sesiones y la presentación de la página principal.

Elementos clave:

1. **Iniciación de sesión**: El código `session_start();` inicia una nueva sesión o reanuda una existente para almacenar información sobre el usuario autenticado.

2. **Verificación de sesión**: La línea `if(!isset($_SESSION['usuario'])){ header("Location: iniciarsesion/index.html"); exit; }` verifica si la variable de sesión `$_SESSION['usuario']` está definida. Si no está definida, redirige al usuario a la página de inicio de sesión.

3. **Carga de estilos**: El archivo incluye un enlace para el archivo CSS llamado "estilo.css" que se encuentra en la carpeta "comun".

4. **Presentación de la página principal**: La estructura HTML proporciona la plantilla básica de una página web, incluyendo la cabecera y el contenido central.

5. **Inclución de archivos PHP**: El archivo utiliza `include` para cargar otros archivos PHP que contienen las funciones específicas de la aplicación, como la cabecera y la lista de modulos.

6. **Redirección a inicio de sesión**: Si no hay una sesión activa, el usuario es redirig

```php
<?php 
  session_start();
  if(!isset($_SESSION['usuario'])){
    header("Location: iniciarsesion/index.html");
    exit;
  }
?>
<!doctype html>
<html lang="es">
  <head>
    <title>ERP Joshue Daniel </title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="comun/estilo.css">
  </head>
  <body>
    <?php include "cabecera/index.php" ?>
    <?php include "listadodemodulos/index.php" ?>
    
  </body>
</html> 
```
#### cabecera
#### comun
#### escritorio
#### iniciarsesion
#### listadodemodulos
#### plantillas
### base de datos
#### instalacion.sql
### documentacion
#### arbol.py

Este archivo `arbol.py` es una implementación de un algoritmo recursivo para generar un árbol visual del contenido de un directorio. Su función principal es mostrar la estructura del directorio en forma gráfica, permitiendo ver los archivos y subdirectorios de manera clara.

Elementos clave:
- `list_entries`: Función que lista todos los elementos (archivos y subdirectorios) dentro de un directorio.
- `draw_tree`: Función recursiva que construye el árbol visual. Utiliza símbolos Unicode para mejorar la presentación gráfica.
- Parámetros: Permite configurar opciones como mostrar archivos ocultos, limitar profundidad del árbol y usar emojis en la representación.

El archivo utiliza bibliotecas como `os` y `typing` para interactuar con el sistema operativo y manejar tipos de datos.

```python
import os
from typing import Iterable, Optional, List

def list_entries(path: str, show_hidden: bool = False) -> Iterable[os.DirEntry]:
    with os.scandir(path) as it:
        entries = [e for e in it if show_hidden or not e.name.startswith(".")]
    entries.sort(key=lambda e: (e.is_file(), e.name.casefold()))
    return entries

def draw_tree(
    path: str,
    prefix: str = "",
    show_hidden: bool = False,
    max_depth: Optional[int] = None,
    _is_last: bool = True,
    _is_root: bool = True,
    use_unicode: bool = True,   # NUEVO
    use_emojis: bool = True,    # NUEVO
) -> List[str]:
    lines: List[str] = []

    name = os.path.basename(os.path.normpath(path)) or path

    elbow_last = "└─" if use_unicode else "\\-"
    elbow_mid  = "├─" if use_unicode else "+-"
    elbow = elbow_last if _is_last else elbow_mid

    folder_icon = "📁" if use_emojis else ""
    file_icon   = "📄" if use_emojis else ""
    link_icon   = "🔗" if use_emojis else ""

    # Root line
    if _is_root:
        lines.append(f"{folder_icon}{name}" if folder_icon else name)
    else:
        lines.append(f"{prefix}{elbow} {folder_icon}{name}".rstrip())

    if max_depth is not None and max_depth <= 0:
        return lines

    child_prefix = prefix + ("   " if _is_last else ("│  " if use_unicode else "|  "))

    try:
        entries = list_entries(path, show_hidden=show_hidden)
    except PermissionError:
        lines.append(f"{child_prefix}{elbow_last} ⛔ (permiso denegado)")
        return lines
    except FileNotFoundError:
        lines.append(f"{child_prefix}{elbow_last} ⚠️  (no encontrado)")
        return lines

    dirs  = [e for e in entries if e.is_dir(follow_symlinks=False)]
    files = [e for e in entries if e.is_file(follow_symlinks=False)]
    others= [e for e in entries if not e.is_dir(follow_symlinks=False) and not e.is_file(follow_symlinks=False)]

    for i, d in enumerate(dirs):
        last = (i == len(dirs) - 1) and not files and not others
        lines.extend(
            draw_tree(
                d.path,
                prefix=child_prefix,
                show_hidden=show_hidden,
                max_depth=None if max_depth is None else max_depth - 1,
                _is_last=last,
                _is_root=False,
                use_unicode=use_unicode,
                use_emojis=use_emojis,
            )
        )

    all_leaves = files + others
    for i, f in enumerate(all_leaves):
        last = (i == len(all_leaves) - 1)
        leaf_elbow = elbow_last if last else elbow_mid
        icon = file_icon if f.is_file(follow_symlinks=False) else link_icon
        lines.append(f"{child_prefix}{leaf_elbow} {icon}{f.name}".rstrip())

    return lines




```
#### cabeceras.py

Este archivo `cabeceras.py` es un script Python que proporciona funciones para listar y manipular archivos en una carpeta. Su función principal es facilitar la gestión de archivos, incluyendo listado de archivos y directorios, creación de enlaces relativos, inferencia de idiomas de archivos basados en extensiones, y filtrado de código según diferentes criterios.

Elementos clave:
- `list_entries`: Lista todos los elementos (archivos y directorios) en una carpeta.
- `_md_escape`: Escapa caracteres para evitar problemas en Markdown.
- `_rel_link`: Crea un enlace relativo entre dos rutas.
- `_infer_lang_from_ext`: Infere el idioma de un archivo basándose en su extensión.

El script se utiliza principalmente para automatizar tareas de gestión de archivos, como listar y manipular contenido en una carpeta.

~~~python
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

~~~
#### cabeceras\_stream.py

Este archivo, `cabeceras_stream.py`, se utiliza para generar un índice de archivos Markdown en tiempo real mientras se generan. Además, proporciona una funcionalidad para documentar cada archivo con la ayuda de Ollama/Qwen, teniendo en cuenta el contexto del proyecto completo.

### Explicación

Este archivo es crucial para mantener un registro detallado y actualizado de los archivos que forman parte de un proyecto. Al generar el índice, se asegura que todos los archivos, incluyendo aquellos ocultos (si se permiten), sean incluidos en la lista.

### Función Principal

El archivo principal es responsable de:
1. Listar y procesar todos los archivos del directorio actual.
2. Generar un índice Markdown que refleje el contenido de cada archivo.
3. Utilizar Ollama/Qwen para documentar cada archivo, proporcionando contexto sobre el proyecto.

### Elementos Clave

- **Listado de Archivos**: Se utiliza `os.scandir` para listar todos los archivos y directorios en el directorio actual.
- **Generación del Indice Markdown**: Se crea un índice Markdown que muestra el nombre y la ruta de cada archivo.
- **Documentación con Ollama/Qwen**: El archivo utiliza la biblioteca `docai` para generar una documentación basada en el contenido del código. Si no se encuentra `docai`, falla al intentar usar

~~~python
# cabeceras_stream.py
# Stream Markdown index to disk as it's generated, and ask Ollama/Qwen
# to document each file with awareness of the whole project's structure.

import os
from typing import Iterable, Optional, Set, Dict, TextIO, List

# ==== Optional: AI documentation (Ollama/Qwen) ====
# We support either:
# - docai.document_code_with_project + docai.build_project_context   (preferred)
# - docai.document_code_with_ollama                                  (fallback, builds prompt here)
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
    project_context: Optional[str] = None,      # pass in to reuse across calls
    project_ctx_allowed_exts: Optional[Set[str]] = None,  # which exts to include in project snapshot
    project_ctx_max_file_bytes: int = 50_000,   # per-file cap inside snapshot
    project_ctx_max_chars: Optional[int] = 400_000,  # final char cap for snapshot (avoid overlong prompts)
    _current_depth: int = 0,
    _root_dir: Optional[str] = None,
) -> None:
    """
    Stream the Markdown for `path` directly to `out`, flushing as we go.
    Reuses a single `project_context` for all files so the model can reason
    about each file's role within the whole project.
    """
    # Build/context once at the top-level if needed
    if _root_dir is None:
        _root_dir = os.path.abspath(path)
    if use_ai_doc and _DOC_AI_AVAILABLE and project_context is None and _current_depth == 0:
        # Prefer external builder from docai.py; otherwise local fallback
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

    def _ai_doc_lines(filename: str, content: str, ext: str) -> List[str]:
        if not use_ai_doc or not _DOC_AI_AVAILABLE:
            return []
        try:
            if _DOC_AI_WITH_PROJECT and project_context is not None:
                md = _doc_ai_with_project(filename=filename, code=content, ext=ext, project_context=project_context)
                return md.strip().splitlines()
            elif _doc_ai_simple is not None:
                # Fallback: build a prompt in-process that includes compact project context
                prompt = f"""Eres un asistente técnico.

Contexto del PROYECTO (resumen):
{project_context or "(no context available)"}

Ahora concéntrate en este archivo:

ARCHIVO: {filename}  (extensión: {ext})
CÓDIGO:
{content}

Tarea:
- Explica qué hace este archivo.
- Describe su papel dentro del proyecto (dependencias y relaciones).
- Usa Markdown en español, hasta 10 viñetas. No repitas el código.
"""
                md = _doc_ai_simple(prompt)  # returns plain markdown
                return (md or "").strip().splitlines()
            else:
                return []
        except Exception as e:
            return [f"> ⚠️ No se pudo generar documentación automática para {filename}: {e}"]

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
                    for ln in ai: write_line(out, ln)

                # Code block
                write_line(out)
                for ln in _fenced_block(content, lang, escape_html_in_fences=escape_html):
                    write_line(out, ln)
    else:
        # Bulleted list; keep Markdown rules (blank + 4-space indent for blocks)
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

                # AI doc (indented)
                ai = _ai_doc_lines(f.name, content, ext)
                if ai:
                    write_line(out)
                    for ln in ai:
                        write_line(out, ("    " + ln) if ln else "    ")

                # Code block (indented)
                write_line(out)
                for ln in _fenced_block(content, lang, escape_html_in_fences=escape_html):
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
            project_context=project_context,  # reuse the same snapshot!
            project_ctx_allowed_exts=project_ctx_allowed_exts,
            project_ctx_max_file_bytes=project_ctx_max_file_bytes,
            project_ctx_max_chars=project_ctx_max_chars,
            _current_depth=_current_depth + 1,
            _root_dir=_root_dir,
        )

# === example direct run ===
if __name__ == "__main__":
    root = "."
    with open("erp.md", "w", encoding="utf-8") as f:
        write_markdown_stream(
            f, root,
            show_hidden=False,
            max_depth=None,
            base_level=1,
            files_as_headings=False,            # or True for headings per file
            link_files=True,
            allowed_extensions={"js","py","md","html","css","php"},
            max_file_bytes=200_000,
            lang_override=None,
            use_emojis=False,                   # ASCII-safe if your viewer isn't UTF-8
            escape_html_for_exts={"html","htm","xml","xhtml","svg"},
            use_ai_doc=True,                    # requires docai.py + Ollama running
            ai_only_when_allowed_ext=True,
            # project context tuning (to keep prompts reasonable)
            project_ctx_allowed_exts={"py","js","ts","tsx","jsx","html","css","md","php","json","yaml","yml","xml","sql","sh"},
            project_ctx_max_file_bytes=50_000,
            project_ctx_max_chars=400_000,
        )

~~~
#### docai.py
