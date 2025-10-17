# documentacion.py
from arbol import draw_tree
from cabeceras_stream import write_markdown_stream

ruta = "..\\"
salida = "erp.md"

with open(salida, "w", encoding="utf-8") as f:
    # 1) Árbol (si quieres que también salga "en vivo"):
    for line in draw_tree(ruta, show_hidden=False, max_depth=None):
        f.write(line + "\n")
        f.flush()

    # 2) Markdown index streaming (AI doc + code fences)
    write_markdown_stream(
        f, ruta,
        show_hidden=False,
        max_depth=None,
        base_level=1,
        files_as_headings=False,     # or True
        link_files=True,
        allowed_extensions={"js","py","md","html","css","php"},
        max_file_bytes=200_000,
        lang_override=None,
        use_emojis=False,            # ASCII-safe if your viewer isn’t UTF-8
        escape_html_for_exts={"html","htm","xml","xhtml","svg"},
        use_ai_doc=True,             # requires docai.py + Ollama up
        ai_only_when_allowed_ext=True,
    )
