from flask import Flask, request
from mifuncion2 import miInterfaz, tablaInterfaz

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    # GET -> muestra formulario, POST -> inserta datos
    return miInterfaz("interfaz.xml")

@app.route('/tabla')
def tabla():
    # Tabla con todos los registros guardados
    return tablaInterfaz("interfaz.xml")

if __name__ == '__main__':
    app.run(debug=True)
