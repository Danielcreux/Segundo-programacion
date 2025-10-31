from flask import Flask, request, jsonify, render_template
import os
import webbrowser
from threading import Timer

app = Flask(__name__)

# ====== Security / Config ======
# Limit file access to a base directory (change to what you need).
BASE_DIR = os.path.abspath(os.getenv("BASE_DIR", os.getcwd()))

TOOLS = [
    {
        "type": "list_files",
        "label": "List files in folder",
        "description": "List immediate files inside a folder (non-recursive).",
        "config": {
            "path": {"type": "string", "label": "Folder path (within BASE_DIR)", "default": ""}
        }
    }
]

def safe_join(base, target):
    # Prevent path traversal outside BASE_DIR
    final_path = os.path.abspath(os.path.join(base, target))
    if not final_path.startswith(base):
        raise ValueError("Path escapes BASE_DIR")
    return final_path

# ====== Routes ======
@app.route("/")
def index():
    # Pass BASE_DIR for UI info
    return render_template("index.html", base_dir=BASE_DIR)

@app.route("/api/tools", methods=["GET"])
def api_tools():
    return jsonify({"tools": TOOLS, "base_dir": BASE_DIR})

@app.route("/api/execute", methods=["POST"])
def api_execute():
    """
    Expected payload:
    {
      "nodes":[{"id":"n1","type":"list_files","config":{"path":"docs"}}],
      "edges":[{"from":"n1","to":"n2"}]
    }
    Returns:
    {
      "results": {"n1": {"ok":true,"data":{...},"error":null}, ...}
    }
    """
    payload = request.get_json(silent=True) or {}
    nodes = payload.get("nodes", [])
    # edges = payload.get("edges", [])  # Not needed yet, but here if you want to route outputs later

    results = {}

    for node in nodes:
        nid = node.get("id")
        ntype = node.get("type")
        config = node.get("config", {})
        try:
            if ntype == "list_files":
                requested = config.get("path", "")
                # Empty string means BASE_DIR itself
                target_dir = safe_join(BASE_DIR, requested)
                if not os.path.isdir(target_dir):
                    raise FileNotFoundError(f"Not a directory: {requested}")

                entries = []
                for name in os.listdir(target_dir):
                    full = os.path.join(target_dir, name)
                    entries.append({
                        "name": name,
                        "is_dir": os.path.isdir(full),
                        "size": os.path.getsize(full) if os.path.isfile(full) else None
                    })

                results[nid] = {"ok": True, "data": {"files": entries, "path": requested}, "error": None}
            else:
                results[nid] = {"ok": False, "data": None, "error": f"Unknown node type: {ntype}"}
        except Exception as e:
            results[nid] = {"ok": False, "data": None, "error": str(e)}

    return jsonify({"results": results})

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Auto-open browser shortly after server starts
    Timer(0.75, open_browser).start()
    app.run(debug=True)
