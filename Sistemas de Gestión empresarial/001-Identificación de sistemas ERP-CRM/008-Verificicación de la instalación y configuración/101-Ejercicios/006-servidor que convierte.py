from flask import Flask
from mifuncion import miInterfaz

app = Flask(__name__)

@app.route('/')
def home():
    return miInterfaz("interfaz.xml")

if __name__ == '__main__':
    app.run()
