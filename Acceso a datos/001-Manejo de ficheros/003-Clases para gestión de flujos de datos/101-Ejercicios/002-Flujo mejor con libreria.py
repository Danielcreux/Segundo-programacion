import pickle

datos = "soy un texto"

#Primero voy a guardar 

archivo = open("datos.bin",'wb')
pickle.dump(datos,archivo)
archivo.close()

#Ahora voy a leer

archivo = open("datos.bin",'rb')
contenido=pickle.load(archivo)
print(contenido)