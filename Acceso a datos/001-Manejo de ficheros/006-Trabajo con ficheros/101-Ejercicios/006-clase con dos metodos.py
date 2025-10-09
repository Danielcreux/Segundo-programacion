class GestorCSV:
    def __init__(self, archivo="clientes.csv"):
        self.archivo = archivo

    def escribir(self, tupla):
        """Escribe una tupla en el archivo CSV"""
        with open(self.archivo, 'a') as f:
            cadena = ",".join(tupla) + "\n"
            f.write(cadena)

    def leer(self):
        """Lee la primera línea del archivo CSV y la devuelve como tupla"""
        with open(self.archivo, 'r') as f:
            linea = f.readline().strip()
            if linea:  # para evitar errores si el archivo está vacío
                campos = linea.split(",")
                return tuple(campos)
            return ()

# Crear instancia
gestor = GestorCSV()

# Escribir una tupla
gestor.escribir(("Joshue Daniel", "Freire", "info@joshue.com"))

# Leer la primera línea como tupla
resultado = gestor.leer()
print(resultado)      
print(type(resultado))  # <class 'tuple'>
