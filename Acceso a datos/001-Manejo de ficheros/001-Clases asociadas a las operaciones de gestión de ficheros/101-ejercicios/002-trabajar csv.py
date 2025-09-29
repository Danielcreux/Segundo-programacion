import csv

# Primero escribo datos

datos = [
    ['nombre','apellidos','telefono'],
    ['Jose','Lopez','53636363'],
    ['Jorge','Rodriguez','53636363'],
    ['Jaime','Perez','53636363'],
    ['Jose','Lopez','53636363'],
    
]

archivo=open("datos.csv",'w')
escritor = csv.writer(archivo)
escritor.writeows(datos)
archivo.close()

# Ahora leo los datos

archivo=open("datos.csv",'r')
lector = csv.reader(archivo)
for linea in lector:
    print(linea)
