import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="blog2526",
    password="blog2526",
    database="blog2526"
)

cursor = conexion.cursor()

cursor.execute("SELECT * FROM libros")

filas = cursor.fetchall()
for fila in filas:
  print(fila)

cursor.close()
conexion.close()

