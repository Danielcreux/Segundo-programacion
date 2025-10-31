# modules/copiarencarpeta.py
import os
import shutil
from typing import Dict, Any, List

TOOL = {
    "type": "copiarencarpeta",
    "label": "Copy into folder",
    "description": "Copies an input list of files into the destination folder (within BASE_DIR).",
    "config": {
        "dest": {"type": "string", "label": "Destination folder (within BASE_DIR)", "default": ""}
    }
}

def _normalize_items_from_inputs(inputs: List[Dict[str, Any]], base_dir: str, safe_join):
    """
    Accepts inputs in several shapes and returns a list of ABSOLUTE file paths within BASE_DIR:

    A) Output from listarcarpetas:
       {"files":[{"name": "...", "is_dir": bool, "size": int|None}, ...], "path":"subdir"}
    B) Plain list of strings:
       ["a.txt", "sub/b.png"]
    C) Dict with 'items':
       {"items": ["a.txt", "sub/b.png"]}

    NOTE: Only files are considered (directories are ignored).
    """
    items: List[str] = []

    for inp in inputs or []:
        # A) listarcarpetas output
        if isinstance(inp, dict) and "files" in inp and "path" in inp:
            src_dir = safe_join(base_dir, inp.get("path", "") or "")
            for f in inp.get("files", []):
                if not isinstance(f, dict):
                    continue
                name = f.get("name")
                if not name:
                    continue
                full = safe_join(src_dir, name)
                if os.path.isfile(full):
                    items.append(full)

        # C) dict with 'items'
        elif isinstance(inp, dict) and "items" in inp:
            for p in (inp["items"] or []):
                if not isinstance(p, str):
                    continue
                full = safe_join(base_dir, p)
                if os.path.isfile(full):
                    items.append(full)

        # B) plain list of strings
        elif isinstance(inp, list):
            for p in inp:
                if not isinstance(p, str):
                    continue
                full = safe_join(base_dir, p)
                if os.path.isfile(full):
                    items.append(full)

        # other shapes ignored

    # deduplicate preserving order
    seen = set()
    dedup: List[str] = []
    for p in items:
        if p not in seen:
            seen.add(p)
            dedup.append(p)
    return dedup

def execute(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Copies files provided via upstream inputs into a destination folder under BASE_DIR.

    config:  {"dest": "<relative folder>"}
    context: {"BASE_DIR": str, "safe_join": callable, "inputs": list}
    """
    base_dir  = context["BASE_DIR"]
    safe_join = context["safe_join"]
    inputs    = context.get("inputs", [])

    dest_rel = (config.get("dest") or "").strip()
    if not dest_rel:
        raise ValueError("Destination folder (dest) is required")

    dest_abs = safe_join(base_dir, dest_rel)
    os.makedirs(dest_abs, exist_ok=True)

    items = _normalize_items_from_inputs(inputs, base_dir, safe_join)
    if not items:
        return {
            "copied": 0,
            "dest": dest_rel,
            "skipped": [],
            "note": "No input files to copy."
        }

    copied = 0
    skipped = []
    for src in items:
        try:
            fname = os.path.basename(src)
            dst = safe_join(dest_abs, fname)
            shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            skipped.append({"file": src, "error": str(e)})

    return {"copied": copied, "dest": dest_rel, "skipped": skipped}
