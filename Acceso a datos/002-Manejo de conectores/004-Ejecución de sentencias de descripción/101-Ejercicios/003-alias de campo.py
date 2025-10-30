import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="accesoadatos2526",
    password="Accesoadatos2526$",
    database="accesoadatos2526"
)

cursor = conexion.cursor()

cursor.execute('''
  SELECT 
  nombre AS "Nombre del cliente",
  apellidos AS "Apellidos del cliente",
  email AS "Email del cliente"
   FROM clientes;
''')

filas = cursor.fetchall()

for fila in filas:
    print(fila)

cursor.close()
conexion.close()