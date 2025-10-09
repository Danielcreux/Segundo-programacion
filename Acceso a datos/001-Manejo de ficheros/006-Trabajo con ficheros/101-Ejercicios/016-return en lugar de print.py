import os
from typing import Iterable, Optional, List

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
) -> List[str]:
    """
    Returns a list of strings that represent the tree of `path`.
    """
    lines = []

    name = os.path.basename(os.path.normpath(path)) or path
    elbow = "└─" if _is_last else "├─"
    icon = "📁"

    # Root line (no elbow for the very first line)
    if _is_root:
        lines.append(f"{icon}{name}")
    else:
        lines.append(f"{prefix}{elbow} {icon}{name}")

    # Stop if depth limit reached
    if max_depth is not None and max_depth <= 0:
        return lines

    child_prefix = prefix + ("   " if _is_last else "│  ")

    try:
        entries = list_entries(path, show_hidden=show_hidden)
    except PermissionError:
        lines.append(f"{child_prefix}└─ ⛔ (permiso denegado)")
        return lines
    except FileNotFoundError:
        lines.append(f"{child_prefix}└─ ⚠️  (no encontrado)")
        return lines

    dirs = [e for e in entries if e.is_dir(follow_symlinks=False)]
    files = [e for e in entries if e.is_file(follow_symlinks=False)]
    others = [e for e in entries if not e.is_dir(follow_symlinks=False) and not e.is_file(follow_symlinks=False)]

    # Recurse directories
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
            )
        )

    # Print files and others
    all_leaves = files + others
    for i, f in enumerate(all_leaves):
        last = (i == len(all_leaves) - 1)
        leaf_elbow = "└─" if last else "├─"
        icon = "📄" if f.is_file(follow_symlinks=False) else "🔗"
        lines.append(f"{child_prefix}{leaf_elbow} {icon}{f.name}")

    return lines


# === Usage ===
ruta = "C:\\xampp\\htdocs\\Segundo-programacion"
tree_lines = draw_tree(ruta, show_hidden=False, max_depth=None)

# Print to screen
print("\n".join(tree_lines))

# Or save to file
with open("tree.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(tree_lines))
