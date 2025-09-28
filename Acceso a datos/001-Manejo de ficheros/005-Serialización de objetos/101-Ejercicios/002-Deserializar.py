import json 

archivo = open("basededatos.dat", 'r')
linea = archivo.readlines()[0]
print(linea)
print(type(linea))
archivo.close()

devuelta = json.loads(linea)
print(devuelta)
print(type(devuelta))