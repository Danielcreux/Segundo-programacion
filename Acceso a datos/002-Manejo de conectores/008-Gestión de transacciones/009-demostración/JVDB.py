import mysql.connector
import json
from datetime import datetime

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
        # Usar dictionary=True para obtener diccionarios en lugar de tuplas
        cursor_dict = self.conexion.cursor(dictionary=True)
        cursor_dict.execute("SELECT * FROM " + tabla)
        filas = cursor_dict.fetchall()
        cursor_dict.close()
        
        # Convertir objetos datetime a strings
        filas_convertidas = []
        for fila in filas:
            fila_convertida = {}
            for clave, valor in fila.items():
                if isinstance(valor, datetime):
                    fila_convertida[clave] = valor.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    fila_convertida[clave] = valor
            filas_convertidas.append(fila_convertida)
        
        return json.dumps(filas_convertidas, ensure_ascii=False, indent=2)
    
    def tablas(self):
        self.cursor.execute("SHOW TABLES")
        filas = self.cursor.fetchall()
        # MySQL devuelve una tupla con el nombre de cada tabla, así que no hay columnas
        datos = [{"tabla": fila[0]} for fila in filas]
        return json.dumps(datos, ensure_ascii=False, indent=2)

    def buscar(self, tabla, campo, valor):
        """Busca registros donde un campo específico contenga un valor"""
        cursor_dict = self.conexion.cursor(dictionary=True)
        
        # Consulta con WHERE para buscar
        consulta = f"SELECT * FROM {tabla} WHERE {campo} LIKE %s"
        cursor_dict.execute(consulta, (f'%{valor}%',))
        
        filas = cursor_dict.fetchall()
        cursor_dict.close()
        
        # Convertir objetos datetime a strings
        filas_convertidas = []
        for fila in filas:
            fila_convertida = {}
            for clave, valor in fila.items():
                if isinstance(valor, datetime):
                    fila_convertida[clave] = valor.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    fila_convertida[clave] = valor
            filas_convertidas.append(fila_convertida)
        
        return json.dumps(filas_convertidas, ensure_ascii=False, indent=2)