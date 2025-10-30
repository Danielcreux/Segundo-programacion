import pickle

class Cliente():
      def __init__(self,nombre,apellidos,emails):
        self.nombre = nombre
        self.apellidos = apellidos
        self.emails = emails

clientes = []
for _ in range(0,10):
      clientes.append(
        Cliente(
          "Joshue Daniel",
              "Freire",
              ["info@joshue.com","info@freire-sanchez-valencia.es"]
          )
      )

archivo = open("clientes.bin",'wb')
pickle.dump(clientes,archivo)


