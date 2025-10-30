import pickle

class Cliente():
      def __init__(self,nombre,apellidos,emails):
        self.nombre = nombre
        self.apellidos = apellidos
        self.emails = emails
    

archivo = open("clientes.bin",'rb')
clientes = pickle.load(archivo)


print(clientes)