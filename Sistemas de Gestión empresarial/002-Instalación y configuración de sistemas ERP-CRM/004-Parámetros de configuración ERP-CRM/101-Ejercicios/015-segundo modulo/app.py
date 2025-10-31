# app.py
from flask import Flask, request, jsonify, render_template
import os
import webbrowser
from threading import Timer
from collections import defaultdict, deque

# === Dynamic backend modules loader ===
# (expects modules/__init__.py to expose load_backend_modules)
from modules import load_backend_modules

app = Flask(__name__, static_folder="static", template_folder="templates")

# ---------- Config ----------
BASE_DIR = os.path.abspath(os.getenv("BASE_DIR", os.getcwd()))
BACKEND_MODULES = load_backend_modules()  # dict: type -> {"TOOL": dict, "execute": callable}


# ---------- Helpers ----------
def static_front_module_exists(tool_type: str) -> bool:
    """Check if a matching front module exists under static/modules/<type>.js"""
    path = os.path.join(app.static_folder, "modules", f"{tool_type}.js")
    return os.path.isfile(path)

def safe_join(base: str, target: str) -> str:
    """Join and ensure the result stays inside base."""
    final_path = os.path.abspath(os.path.join(base, target))
    if not final_path.startswith(base):
        raise ValueError("Path escapes BASE_DIR")
    return final_path


# ---------- Routes ----------
@app.route("/")
def index():
    # Render the UI
    return render_template("index.html", base_dir=BASE_DIR)


@app.route("/api/tools", methods=["GET"])
def api_tools():
    """
    Return detected tools. Each tool is a dict with:
      {type, label, description, config, [front_module]}
    If a matching front module JS exists (static/modules/<type>.js),
    include its URL so the frontend can import it dynamically.
    """
    tools = []
    for t, mod in BACKEND_MODULES.items():
        tool = dict(mod["TOOL"])  # copy
        if static_front_module_exists(t):
            tool["front_module"] = f"/static/modules/{t}.js"
        tools.append(tool)

    return jsonify({"tools": tools, "base_dir": BASE_DIR})


@app.route("/api/execute", methods=["POST"])
def api_execute():
    """
    Execute the graph in topological order.

    Payload:
    {
      "nodes":[{"id":"n1","type":"listarcarpetas","config":{...}}, ...],
      "edges":[{"from":"n1","to":"n2"}, ...]
    }

    Returns:
    {
      "results": {
        "n1": {"ok":true,"data":{...},"error":null},
        "n2": {"ok":false,"data":null,"error":"..."},
        ...
      }
    }
    """
    payload = request.get_json(silent=True) or {}
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])

    # Index nodes by id
    node_by_id = {n.get("id"): n for n in nodes}

    # Build graph for topological sort (Kahn)
    adj = defaultdict(list)   # from -> [to...]
    indeg = defaultdict(int)  # node_id -> indegree

    for nid in node_by_id.keys():
        indeg[nid] = 0

    for e in edges:
        f = e.get("from")
        t = e.get("to")
        if f in node_by_id and t in node_by_id:
            adj[f].append(t)
            indeg[t] += 1

    q = deque([nid for nid, d in indeg.items() if d == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if len(order) != len(node_by_id):
        return jsonify({"results": {}, "error": "Cycle detected or missing nodes for execution"}), 400

    results = {}  # nid -> {"ok": bool, "data": any, "error": str|None}

    def get_upstream_data(nid: str):
        """Collect successful upstream .data for this node."""
        data_list = []
        for src, tos in adj.items():
            if nid in tos and src in results and results[src]["ok"]:
                data_list.append(results[src]["data"])
        return data_list

    # Execute nodes in order
    for nid in order:
        node = node_by_id[nid]
        ntype = node.get("type")
        config = node.get("config", {})

        try:
            mod = BACKEND_MODULES.get(ntype)
            if not mod:
                raise RuntimeError(f"Unknown node type: {ntype}")

            context = {
                "BASE_DIR": BASE_DIR,
                "safe_join": safe_join,
                "inputs": get_upstream_data(nid),  # pass upstream outputs
            }
            out = mod["execute"](config, context)
            results[nid] = {"ok": True, "data": out, "error": None}
        except Exception as e:
            results[nid] = {"ok": False, "data": None, "error": str(e)}

    return jsonify({"results": results})


# ---------- Dev convenience ----------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    # Auto-open browser shortly after startup
    Timer(0.75, open_browser).start()
    # Run Flask
    app.run(debug=True)
