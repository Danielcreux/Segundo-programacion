import pickle

class Contacto:
    def __init__(self,minombre,mitelefono):
        self.nombre = minombre
        self.telefono =  mitelefono
        
agenda = []

for i in range(0,10):
    agenda.append(Contacto("Joshué Daniel"))
    
print(agenda)

datos = "soy un texto"

#Primero voy a guardar 

archivo = open("datos.bin",'wb')
pickle.dump(datos,archivo)
archivo.close()

#Ahora voy a leer

archivo = open("datos.bin",'rb')
contenido=pickle.load(archivo)
print(contenido)