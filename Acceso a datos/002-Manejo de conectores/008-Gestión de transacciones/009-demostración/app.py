from flask import Flask, render_template
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

if __name__ == "__main__":
    aplicacion.run(debug=True)

