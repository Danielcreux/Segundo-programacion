import os
from typing import Iterable, Optional

def list_entries(path: str, show_hidden: bool = False) -> Iterable[os.DirEntry]:
    with os.scandir(path) as it:
        entries = [e for e in it if show_hidden or not e.name.startswith(".")]
    # Directories first, then files; case-insensitive
    entries.sort(key=lambda e: (e.is_file(), e.name.casefold()))
    return entries

def draw_tree(
    path: str,
    prefix: str = "",
    show_hidden: bool = False,
    max_depth: Optional[int] = None,
    _is_last: bool = True,
    _is_root: bool = True,
):
    name = os.path.basename(os.path.normpath(path)) or path
    elbow = "└─" if _is_last else "├─"
    icon = "📁"

    # Root line (no elbow for the very first line)
    if _is_root:
        print(f"{icon}{name}")
    else:
        print(f"{prefix}{elbow} {icon}{name}")

    # Stop if depth limit reached
    if max_depth is not None and max_depth <= 0:
        return

    # Child prefix: continues the vertical line if not the last sibling
    child_prefix = prefix + ("   " if _is_last else "│  ")

    try:
        entries = list_entries(path, show_hidden=show_hidden)
    except PermissionError:
        print(f"{child_prefix}└─ ⛔ (permiso denegado)")
        return
    except FileNotFoundError:
        print(f"{child_prefix}└─ ⚠️  (no encontrado)")
        return

    # Split dirs/files to print directories first (each will recurse)
    dirs = [e for e in entries if e.is_dir(follow_symlinks=False)]
    files = [e for e in entries if e.is_file(follow_symlinks=False)]
    others = [e for e in entries if not e.is_dir(follow_symlinks=False) and not e.is_file(follow_symlinks=False)]

    # Helper to print a flat node (file or "other")
    def print_leaf(entry: os.DirEntry, last: bool):
        leaf_elbow = "└─" if last else "├─"
        icon = "📄" if entry.is_file(follow_symlinks=False) else "🔗"  # symlink/other
        print(f"{child_prefix}{leaf_elbow} {icon}{entry.name}")

    # Recurse directories
    for i, d in enumerate(dirs):
        last = (i == len(dirs) - 1) and not files and not others
        draw_tree(
            d.path,
            prefix=child_prefix,
            show_hidden=show_hidden,
            max_depth=None if max_depth is None else max_depth - 1,
            _is_last=last,
            _is_root=False,
        )

    # Print files and others
    all_leaves = files + others
    for i, f in enumerate(all_leaves):
        last = (i == len(all_leaves) - 1)
        print_leaf(f, last)

# === Usage ===
ruta = "C:\\xampp\\htdocs\\Segundo-programacion"
draw_tree(ruta, show_hidden=False, max_depth=None)
