import os

class YourSQL():
  def __init__(self):
    self.carpeta_bd = "db"
  def peticion(self,peticion):
    if peticion == "SHOW DATABASES;":
      carpetas = os.listdir(carpeta_bd)
      for carpeta in carpetas:
        print(carpeta)