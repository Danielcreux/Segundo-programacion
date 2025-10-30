import os

carpeta = "C:\\Users\\Valentina\\Desktop\\muchovideos"

archivos = os.listdir(carpeta)

for archivo in archivos:
    print(archivo)