import os

carpeta_bd = "db"

carpetas = os.listdir(carpeta_bd)

for carpeta in carpetas:
    print(carpeta)