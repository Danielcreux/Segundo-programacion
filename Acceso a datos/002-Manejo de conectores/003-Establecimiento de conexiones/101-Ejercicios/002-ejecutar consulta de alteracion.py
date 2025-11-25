import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="accesoadatos2526",
    password="Accesoadatos2526$",
    database="accesoadatos2526"
)

cursor = conexion.cursor()


cursor.execute('''
  ALTER TABLE clientes
  ADD PRIMARY KEY (`Identificador`);
''')

cursor.execute('''
  ALTER TABLE clientes
MODIFY COLUMN Identificador INT NOT NULL AUTO_INCREMENT;
''')

conexion.commit()

cursor.close()
conexion.close()