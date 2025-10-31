import os
from typing import Dict, Any

TOOL = {
    "type": "listarcarpetas",
    "label": "List files in folder",
    "description": "List immediate files inside a folder (non-recursive).",
    "config": {
        "path": {"type": "string", "label": "Folder path (within BASE_DIR)", "default": ""}
    }
}

def execute(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lógica del tool.
    config: {"path": "..."}
    context: {"BASE_DIR": str, "safe_join": callable}
    """
    path = config.get("path", "") or ""
    safe_join = context["safe_join"]
    base_dir = context["BASE_DIR"]

    target_dir = safe_join(base_dir, path)
    if not os.path.isdir(target_dir):
        raise FileNotFoundError(f"Not a directory: {path}")

    entries = []
    for name in os.listdir(target_dir):
        full = os.path.join(target_dir, name)
        entries.append({
            "name": name,
            "is_dir": os.path.isdir(full),
            "size": os.path.getsize(full) if os.path.isfile(full) else None
        })
    return {"files": entries, "path": path}
