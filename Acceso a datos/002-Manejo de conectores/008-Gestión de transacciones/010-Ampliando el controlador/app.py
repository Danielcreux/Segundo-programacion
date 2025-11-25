from flask import Flask, render_template, request, jsonify
from JVDB import JVDB

aplicacion = Flask(__name__)

# Conexión con la base de datos
conexion = JVDB("localhost", "blog2526", "blog2526", "blog2526")

@aplicacion.route("/")
def raiz():
    return render_template("index.html")

# Ruta dinámica: permite seleccionar cualquier tabla
@aplicacion.route("/seleccionar/<tabla>")
def seleccionar(tabla):
    return conexion.seleccionar(tabla)

@aplicacion.route("/tablas")
def tablas():
    return conexion.tablas()

@aplicacion.post("/insertar/<tabla>")
def insertar(tabla):
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"error": True, "mensaje": "JSON inválido"}), 400

    def _clean_row(d):
        # Convierte '' -> None para que MySQL trate como NULL
        return {k: (None if isinstance(v, str) and v.strip() == "" else v) for k, v in d.items()}

    if isinstance(payload, list):
        datos = [_clean_row(d) for d in payload if isinstance(d, dict)]
    elif isinstance(payload, dict):
        datos = _clean_row(payload)
    else:
        return jsonify({"error": True, "mensaje": "El cuerpo debe ser un objeto o lista de objetos"}), 400

    # `insertar` ya devuelve un JSON (string). Lo devolvemos con el mimetype adecuado.
    res = conexion.insertar(tabla, datos)
    return aplicacion.response_class(res, mimetype="application/json")

if __name__ == "__main__":
    aplicacion.run(debug=True)

