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



