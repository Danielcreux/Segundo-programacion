import os

class YourSQL:
  carpeta_bd = "db"
  base_actual = ""

  @staticmethod
  def peticion(peticion):
    if peticion == "SHOW DATABASES;":
      carpetas = os.listdir(YourSQL.carpeta_bd)
      for carpeta in carpetas:
        print(carpeta)
    elif "USE" in peticion:
      YourSQL.base_actual = peticion.split(" ")[1].split(";")[0]
    elif peticion == "SHOW TABLES;":
      tablas = os.listdir(YourSQL.carpeta_bd+"/"+YourSQL.base_actual)
      for tabla in tablas:
        print(tabla)
            
YourSQL.peticion("USE accesoadatos;")
YourSQL.peticion("SHOW TABLES;")
