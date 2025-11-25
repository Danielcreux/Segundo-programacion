import json
import mysql.connector
from datetime import datetime, date, time

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        return super().default(obj)

class ConexionBD:
    def __init__(self):
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="blog2526",
            password="blog2526",
            database="blog2526"
        )
    
    def seleccionar(self, tabla):
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {tabla}")
        filas = cursor.fetchall()
        cursor.close()
        
        # Usar el encoder personalizado
        return json.dumps(filas, cls=DateTimeEncoder, ensure_ascii=False, indent=2)

# Uso
conexion = ConexionBD()
print(conexion.seleccionar("libros"))