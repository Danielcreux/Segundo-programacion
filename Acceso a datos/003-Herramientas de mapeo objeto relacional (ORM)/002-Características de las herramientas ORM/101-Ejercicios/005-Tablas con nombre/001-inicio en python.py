import mysql.connector
import json

class JVDB():
  def __init__(self, host, usuario, contrasena, basedatos):
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

  def seleccionar(self, tabla):
    self.cursor.execute(f"SELECT * FROM {tabla}")
    columnas = self.cursor.column_names
    filas = self.cursor.fetchall()
    datos = [dict(zip(columnas, fila)) for fila in filas]
    return json.dumps(datos, ensure_ascii=False, indent=2)

  def buscar(self, tabla, columna, valor):
    sql = f"SELECT * FROM {tabla} WHERE {columna} LIKE %s"
    self.cursor.execute(sql, (f"%{valor}%",))
    columnas = self.cursor.column_names
    filas = self.cursor.fetchall()
    datos = [dict(zip(columnas, fila)) for fila in filas]
    return json.dumps(datos, ensure_ascii=False, indent=2)

# Ejemplo de uso
conexion = JVDB("localhost", "blog2526", "blog2526", "blog2526")
print(conexion.buscar("entradas", "titulo", "responsivo"))
