import os

class YourSQL:
    carpeta_bd = "db"

    @staticmethod
    def peticion(peticion):
        if peticion == "SHOW DATABASES;":
            carpetas = os.listdir(YourSQL.carpeta_bd)
            for carpeta in carpetas:
                print(carpeta)

YourSQL.peticion("SHOW DATABASES;")
