import mysql.connector

class JVDB():
  def __init__(self,host,usuario,contrasena,basedatos):
    self.host = host
    self.usuario = usuario
    self.contrasena = contrasena
    self.basedatos = basedatos

    self.conexion = mysql.connector.connect(
        host=self.host,
        user=self.usuario,
        password=self.contrasena,
        database=self.basedatos
    )

    self.cursor = self.conexion.cursor()

  def seleccionar(self,tabla):
    self.cursor.execute("SELECT * FROM "+tabla)
    filas = self.cursor.fetchall()
    for fila in filas:
      print(fila)
    
conexion = JVDB("localhost","blog2526","blog2526","blog2526")
conexion.seleccionar("libros")
   

