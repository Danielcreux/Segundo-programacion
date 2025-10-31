from flask import Flask, request, jsonify, render_template
import os
import webbrowser
from threading import Timer
from collections import defaultdict, deque
from typing import Dict, Any, List, Tuple

from modules import load_backend_modules

app = Flask(__name__, static_folder="static", template_folder="templates")

# ===== Config (hardcoded, acceso total) =====
BASE_DIR = "/"          # raíz del sistema
ALLOW_ANY_PATH = True   # permite rutas absolutas en todo el FS

BACKEND_MODULES = load_backend_modules()


def static_front_module_exists(tool_type: str) -> bool:
    path = os.path.join(app.static_folder, "modules", f"{tool_type}.js")
    return os.path.isfile(path)


def safe_join(base: str, target: str, allow_abs: bool = False) -> str:
    """
    Si allow_abs=True y target es absoluto, se permite (normalizado).
    Si no, se une base+target y se asegura de no salir de base.
    """
    if allow_abs and os.path.isabs(target):
        return os.path.abspath(target)

    p = os.path.abspath(os.path.join(base, target))
    # Si base es "/" (unix), cualquier abs path empieza por "/" -> OK
    # Si no, se confina a base
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


# === Ligero explorador de FS para el folder picker ===
@app.route("/api/fs/list", methods=["GET"])
def api_fs_list():
    """
    Query params:
      path: carpeta a listar ('' implica BASE_DIR)
    Devuelve subdirectorios y archivos (nombre + ruta absoluta cuando ALLOW_ANY_PATH, si no relativa a BASE_DIR).
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

        # dirs primero, luego ficheros
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        parent = os.path.abspath(os.path.join(root, os.pardir))
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
    nodes: List[Dict[str, Any]] = payload.get("nodes", [])
    edges: List[Dict[str, Any]] = payload.get("edges", [])

    # índice por id
    node_by_id: Dict[str, Dict[str, Any]] = {n.get("id"): n for n in nodes}

    # Grafo dirigido con conservación de from_port en las aristas:
    # adj[src] = lista de (to_id, from_port)
    adj: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    indeg: Dict[str, int] = defaultdict(int)
    for nid in node_by_id:
        indeg[nid] = 0

    for e in edges:
        f = e.get("from")
        t = e.get("to")
        fp = e.get("from_port")  # puede ser None -> "default" en lectura
        if f in node_by_id and t in node_by_id:
            adj[f].append((t, fp))
            indeg[t] += 1

    # Orden topológico (Kahn)
    q = deque([nid for nid, d in indeg.items() if d == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for (v, _fp) in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if len(order) != len(node_by_id):
        return jsonify({"results": {}, "error": "Cycle detected or missing nodes for execution"}), 400

    results: Dict[str, Dict[str, Any]] = {}

    # Para leer entradas de un nodo respetando from_port y rutas nombradas
    def upstream_data(nid: str) -> List[Any]:
        lst: List[Any] = []
        # hallamos todos los predecesores que apuntan a nid
        for src, tos in adj.items():
            for (to_id, fp) in tos:
                if to_id != nid:
                    continue
                if src not in results or not results[src]["ok"]:
                    continue
                rp = results[src]["data"]
                from_port = fp or "default"
                # Si el resultado trae rutas nombradas, solo entregamos la ruta que coincide
                if isinstance(rp, dict) and "routes" in rp and isinstance(rp["routes"], dict):
                    if from_port in rp["routes"]:
                        routed_val = rp["routes"][from_port]
                        if routed_val is not None:
                            lst.append(routed_val)
                else:
                    # Sin rutas, pasamos el dato "plano"
                    lst.append(rp)
        return lst

    # Ejecutamos en orden
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
    # Acceso total ya está hardcodeado arriba.
    Timer(0.75, open_browser).start()
    app.run(debug=True)
