# app.py (only the changed/added parts)

from flask import Flask, request, jsonify, render_template
import os
import webbrowser
from threading import Timer
from collections import defaultdict, deque

from modules import load_backend_modules

app = Flask(__name__, static_folder="static", template_folder="templates")

# ===== Config =====
BASE_DIR = os.path.abspath(os.getenv("BASE_DIR", os.getcwd()))
ALLOW_ANY_PATH = os.getenv("ALLOW_ANY_PATH", "0") in ("1", "true", "True")

BACKEND_MODULES = load_backend_modules()

def static_front_module_exists(tool_type: str) -> bool:
    path = os.path.join(app.static_folder, "modules", f"{tool_type}.js")
    return os.path.isfile(path)

def safe_join(base: str, target: str, allow_abs: bool = False) -> str:
    """
    If allow_abs is True and target is absolute, allow it (normalized).
    Otherwise join base+target and ensure it stays inside base.
    """
    if allow_abs and os.path.isabs(target):
        p = os.path.abspath(target)
        return p
    p = os.path.abspath(os.path.join(base, target))
    # If base is "/" (unix), every abs path startswith("/") -> OK
    # Otherwise enforce base confinement
    if base != os.path.sep and not p.startswith(base):
        raise ValueError("Path escapes BASE_DIR")
    return p

@app.route("/")
def index():
    return render_template("index.html", base_dir=BASE_DIR)

@app.route("/api/tools", methods=["GET"])
def api_tools():
    tools = []
    for t, mod in BACKEND_MODULES.items():
        tool = dict(mod["TOOL"])
        if static_front_module_exists(t):
            tool["front_module"] = f"/static/modules/{t}.js"
        tools.append(tool)
    return jsonify({
        "tools": tools,
        "base_dir": BASE_DIR,
        "allow_any_path": ALLOW_ANY_PATH
    })

# === NEW: lightweight filesystem browser for the folder picker ===
@app.route("/api/fs/list", methods=["GET"])
def api_fs_list():
    """
    Query params:
      path: folder to list ('' means BASE_DIR)
    Returns subdirectories and files (names + absolute path when ALLOW_ANY_PATH, else rel to BASE_DIR).
    """
    path = request.args.get("path", "").strip()
    try:
        root = safe_join(BASE_DIR, path, allow_abs=ALLOW_ANY_PATH)
        if not os.path.isdir(root):
            return jsonify({"error": f"Not a directory: {path}"}), 400

        items = []
        for name in os.listdir(root):
            full = os.path.join(root, name)
            items.append({
                "name": name,
                "path": full if ALLOW_ANY_PATH else os.path.relpath(full, BASE_DIR),
                "is_dir": os.path.isdir(full)
            })

        # Sort: dirs first, then files
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        parent = os.path.abspath(os.path.join(root, os.pardir))
        # Clamp parent display when not ALLOW_ANY_PATH and parent would escape BASE_DIR
        parent_allowed = True
        if not ALLOW_ANY_PATH and BASE_DIR != os.path.sep and not parent.startswith(BASE_DIR):
            parent_allowed = False

        return jsonify({
            "cwd": root,
            "parent": parent if parent_allowed else None,
            "items": items
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/execute", methods=["POST"])
def api_execute():
    payload = request.get_json(silent=True) or {}
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])

    node_by_id = {n.get("id"): n for n in nodes}
    from collections import defaultdict, deque
    adj = defaultdict(list)
    indeg = defaultdict(int)
    for nid in node_by_id: indeg[nid] = 0
    for e in edges:
        f, t = e.get("from"), e.get("to")
        if f in node_by_id and t in node_by_id:
            adj[f].append(t); indeg[t] += 1

    q = deque([nid for nid,d in indeg.items() if d==0])
    order = []
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v]-=1
            if indeg[v]==0: q.append(v)

    if len(order) != len(node_by_id):
        return jsonify({"results": {}, "error": "Cycle detected or missing nodes for execution"}), 400

    results = {}
    def upstream_data(nid):
        lst=[]
        for src, tos in adj.items():
            if nid in tos and src in results and results[src]["ok"]:
                lst.append(results[src]["data"])
        return lst

    for nid in order:
        node = node_by_id[nid]
        ntype = node.get("type")
        config = node.get("config", {})
        try:
            mod = BACKEND_MODULES.get(ntype)
            if not mod:
                raise RuntimeError(f"Unknown node type: {ntype}")
            ctx = {
                "BASE_DIR": BASE_DIR,
                "safe_join": lambda base, target: safe_join(base, target, allow_abs=ALLOW_ANY_PATH),
                "inputs": upstream_data(nid),
                "ALLOW_ANY_PATH": ALLOW_ANY_PATH,
            }
            out = mod["execute"](config, ctx)
            results[nid] = {"ok": True, "data": out, "error": None}
        except Exception as e:
            results[nid] = {"ok": False, "data": None, "error": str(e)}

    return jsonify({"results": results})


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # If you truly want to select any folder on your machine:
    #   export ALLOW_ANY_PATH=1
    #   export BASE_DIR=/
    Timer(0.75, open_browser).start()
    app.run(debug=True)
