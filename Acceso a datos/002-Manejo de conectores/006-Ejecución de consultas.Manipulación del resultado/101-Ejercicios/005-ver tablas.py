import os

class YourSQL:
  carpeta_bd = "db"

  @staticmethod
  def peticion(peticion):
    if peticion == "SHOW DATABASES;":
      carpetas = os.listdir(YourSQL.carpeta_bd)
      for carpeta in carpetas:
        print(carpeta)
    elif peticion == "SHOW TABLES;":
      tablas = os.listdir(YourSQL.carpeta_bd+"/accesoadatos")
      for tabla in tablas:
        print(tabla)
            

YourSQL.peticion("SHOW TABLES;")
