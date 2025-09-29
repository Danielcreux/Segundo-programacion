import mysql.connector
import json
from typing import Dict, List, Any

def load_json_data(filename: str) -> Dict:
    """Cargar datos desde archivo JSON externo"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filename}'")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: JSON inválido en el archivo '{filename}': {e}")
        return None

def get_mysql_type(value):
    """Determinar el tipo de dato MySQL basado en el valor Python"""
    if value is None:
        return 'VARCHAR(255)'
    elif isinstance(value, str):
        if len(value) > 255:
            return 'TEXT'
        else:
            return 'VARCHAR(255)'
    elif isinstance(value, int):
        return 'INT'
    elif isinstance(value, float):
        return 'DECIMAL(10,2)'
    elif isinstance(value, bool):
        return 'BOOLEAN'
    else:
        return 'VARCHAR(255)'

def create_tables_from_json(json_data):
    """Crear tablas basadas en la estructura JSON"""
    
    # Conectar a la base de datos
    conn = mysql.connector.connect(
        host="localhost",
        user="desfase",
        password="desfase",
        database="desfase"
    )
    cursor = conn.cursor()
    
    # Desactivar verificación de claves foráneas para poder eliminar tablas
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Eliminar tablas existentes en orden inverso
    tables_to_drop = [
        'clientes_empleo_historial_laboral',
        'clientes_empleo_empresa_actual_beneficios',
        'clientes_empleo_empresa_actual',
        'clientes_empleo',
        'clientes_educacion_certificaciones',
        'clientes_educacion_estudios',
        'clientes_educacion',
        'clientes_preferencias_categorias_favoritas',
        'clientes_preferencias_productos_interes',
        'clientes_preferencias_comunicacion',
        'clientes_preferencias',
        'clientes_direcciones_coordenadas',
        'clientes_direcciones',
        'clientes_contacto_redes_sociales',
        'clientes_contacto_telefonos',
        'clientes_contacto_emails',
        'clientes_contacto',
        'clientes_informacion_personal',
        'clientes_metadatos',
        'clientes'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Tabla {table} eliminada")
        except mysql.connector.Error as e:
            print(f"Error eliminando tabla {table}: {e}")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # Crear tablas basadas en la estructura JSON
    create_table_queries = [
        # Tabla principal de clientes
        """
        CREATE TABLE clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL UNIQUE,
            fecha_registro DATETIME,
            fecha_ultima_actualizacion DATETIME,
            estado VARCHAR(50),
            puntuacion_riesgo INT,
            segmento VARCHAR(50)
        )
        """,
        
        # Información personal (1:1 con clientes)
        """
        CREATE TABLE clientes_informacion_personal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL,
            nombre VARCHAR(100),
            apellidos VARCHAR(100),
            dni VARCHAR(20),
            edad INT,
            fecha_nacimiento DATE,
            genero VARCHAR(20),
            nacionalidad VARCHAR(50),
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
        )
        """,
        
        # Tabla de contacto (1:1 con clientes)
        """
        CREATE TABLE clientes_contacto (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
        )
        """,
        
        # Emails (1:N con contacto)
        """
        CREATE TABLE clientes_contacto_emails (
            id INT AUTO_INCREMENT PRIMARY KEY,
            contacto_id INT NOT NULL,
            tipo VARCHAR(50),
            direccion VARCHAR(255),
            verificado BOOLEAN,
            fecha_verificacion DATE,
            preferido BOOLEAN,
            FOREIGN KEY (contacto_id) REFERENCES clientes_contacto(id) ON DELETE CASCADE
        )
        """,
        
        # Teléfonos (1:N con contacto)
        """
        CREATE TABLE clientes_contacto_telefonos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            contacto_id INT NOT NULL,
            tipo VARCHAR(50),
            numero VARCHAR(50),
            pais VARCHAR(10),
            operadora VARCHAR(100),
            activo BOOLEAN,
            fecha_activacion DATE,
            FOREIGN KEY (contacto_id) REFERENCES clientes_contacto(id) ON DELETE CASCADE
        )
        """,
        
        # Redes sociales (1:N con contacto)
        """
        CREATE TABLE clientes_contacto_redes_sociales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            contacto_id INT NOT NULL,
            plataforma VARCHAR(100),
            usuario VARCHAR(100),
            url TEXT,
            seguidores INT,
            verificada BOOLEAN,
            FOREIGN KEY (contacto_id) REFERENCES clientes_contacto(id) ON DELETE CASCADE
        )
        """,
        
        # Direcciones (1:N con clientes)
        """
        CREATE TABLE clientes_direcciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL,
            tipo VARCHAR(50),
            calle VARCHAR(255),
            piso VARCHAR(50),
            codigo_postal VARCHAR(20),
            ciudad VARCHAR(100),
            provincia VARCHAR(100),
            pais VARCHAR(100),
            fecha_registro DATE,
            activa BOOLEAN,
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
        )
        """,
        
        # Coordenadas (1:1 con direcciones)
        """
        CREATE TABLE clientes_direcciones_coordenadas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            direccion_id INT NOT NULL,
            latitud DECIMAL(10,6),
            longitud DECIMAL(10,6),
            FOREIGN KEY (direccion_id) REFERENCES clientes_direcciones(id) ON DELETE CASCADE
        )
        """,
        
        # Empleo (1:1 con clientes)
        """
        CREATE TABLE clientes_empleo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL,
            nivel_maximo VARCHAR(100),
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
        )
        """,
        
        # Empresa actual (1:1 con empleo)
        """
        CREATE TABLE clientes_empleo_empresa_actual (
            id INT AUTO_INCREMENT PRIMARY KEY,
            empleo_id INT NOT NULL,
            nombre VARCHAR(255),
            cargo VARCHAR(100),
            departamento VARCHAR(100),
            fecha_inicio DATE,
            salario_anual DECIMAL(12,2),
            moneda VARCHAR(10),
            tipo_contrato VARCHAR(50),
            jornada VARCHAR(50),
            edificio VARCHAR(100),
            calle VARCHAR(255),
            ciudad VARCHAR(100),
            codigo_postal VARCHAR(20),
            FOREIGN KEY (empleo_id) REFERENCES clientes_empleo(id) ON DELETE CASCADE
        )
        """,
        
        # Beneficios (1:N con empresa_actual)
        """
        CREATE TABLE clientes_empleo_empresa_actual_beneficios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            empresa_actual_id INT NOT NULL,
            beneficio VARCHAR(255),
            FOREIGN KEY (empresa_actual_id) REFERENCES clientes_empleo_empresa_actual(id) ON DELETE CASCADE
        )
        """,
        
        # Historial laboral (1:N con empleo)
        """
        CREATE TABLE clientes_empleo_historial_laboral (
            id INT AUTO_INCREMENT PRIMARY KEY,
            empleo_id INT NOT NULL,
            empresa VARCHAR(255),
            cargo VARCHAR(100),
            fecha_inicio DATE,
            fecha_fin DATE,
            motivo_salida TEXT,
            FOREIGN KEY (empleo_id) REFERENCES clientes_empleo(id) ON DELETE CASCADE
        )
        """,
        
        # Educación (1:1 con clientes)
        """
        CREATE TABLE clientes_educacion (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL,
            nivel_maximo VARCHAR(100),
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
        )
        """,
        
        # Estudios (1:N con educación)
        """
        CREATE TABLE clientes_educacion_estudios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            educacion_id INT NOT NULL,
            titulacion VARCHAR(255),
            institucion VARCHAR(255),
            fecha_inicio DATE,
            fecha_fin DATE,
            puntuacion DECIMAL(4,2),
            especialidad VARCHAR(255),
            FOREIGN KEY (educacion_id) REFERENCES clientes_educacion(id) ON DELETE CASCADE
        )
        """,
        
        # Certificaciones (1:N con educación)
        """
        CREATE TABLE clientes_educacion_certificaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            educacion_id INT NOT NULL,
            nombre VARCHAR(255),
            institucion VARCHAR(255),
            fecha_obtencion DATE,
            fecha_expiracion DATE,
            id_certificacion VARCHAR(100),
            FOREIGN KEY (educacion_id) REFERENCES clientes_educacion(id) ON DELETE CASCADE
        )
        """,
        
        # Preferencias (1:1 con clientes)
        """
        CREATE TABLE clientes_preferencias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id VARCHAR(50) NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
        )
        """,
        
        # Comunicación (1:1 con preferencias)
        """
        CREATE TABLE clientes_preferencias_comunicacion (
            id INT AUTO_INCREMENT PRIMARY KEY,
            preferencias_id INT NOT NULL,
            canal_preferido VARCHAR(50),
            frecuencia_newsletter VARCHAR(50),
            acepta_marketing BOOLEAN,
            idioma VARCHAR(10),
            zona_horaria VARCHAR(50),
            FOREIGN KEY (preferencias_id) REFERENCES clientes_preferencias(id) ON DELETE CASCADE
        )
        """,
        
        # Productos de interés (1:N con preferencias)
        """
        CREATE TABLE clientes_preferencias_productos_interes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            preferencias_id INT NOT NULL,
            producto VARCHAR(100),
            FOREIGN KEY (preferencias_id) REFERENCES clientes_preferencias(id) ON DELETE CASCADE
        )
        """,
        
        # Categorías favoritas (1:N con preferencias)
        """
        CREATE TABLE clientes_preferencias_categorias_favoritas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            preferencias_id INT NOT NULL,
            categoria VARCHAR(100),
            nivel_interes INT,
            ultima_visita DATE,
            FOREIGN KEY (preferencias_id) REFERENCES clientes_preferencias(id) ON DELETE CASCADE
        )
        """
    ]
    
    # Ejecutar las consultas de creación de tablas
    for query in create_table_queries:
        try:
            cursor.execute(query)
            print(f"Tabla creada exitosamente")
        except mysql.connector.Error as e:
            print(f"Error creando tabla: {e}")
    
    conn.commit()
    return conn, cursor

def insert_json_data(cursor, json_data):
    """Insertar datos JSON en las tablas creadas"""
    
    clientes = json_data.get('clientes', [])
    
    for cliente in clientes:
        try:
            # Insertar en tabla principal clientes
            cursor.execute("""
                INSERT INTO clientes (cliente_id, fecha_registro, fecha_ultima_actualizacion, estado, puntuacion_riesgo, segmento)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                cliente.get('id'),
                cliente.get('metadatos', {}).get('fecha_registro'),
                cliente.get('metadatos', {}).get('fecha_ultima_actualizacion'),
                cliente.get('metadatos', {}).get('estado'),
                cliente.get('metadatos', {}).get('puntuacion_riesgo'),
                cliente.get('metadatos', {}).get('segmento')
            ))
            cliente_id = cliente.get('id')
            
            # Información personal
            info_personal = cliente.get('informacion_personal', {})
            if info_personal:
                cursor.execute("""
                    INSERT INTO clientes_informacion_personal 
                    (cliente_id, nombre, apellidos, dni, edad, fecha_nacimiento, genero, nacionalidad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    cliente_id,
                    info_personal.get('nombre'),
                    info_personal.get('apellidos'),
                    info_personal.get('dni'),
                    info_personal.get('edad'),
                    info_personal.get('fecha_nacimiento'),
                    info_personal.get('genero'),
                    info_personal.get('nacionalidad')
                ))
            
            # Contacto
            contacto = cliente.get('contacto', {})
            if contacto:
                cursor.execute("INSERT INTO clientes_contacto (cliente_id) VALUES (%s)", (cliente_id,))
                contacto_id = cursor.lastrowid
                
                # Emails
                for email in contacto.get('emails', []):
                    cursor.execute("""
                        INSERT INTO clientes_contacto_emails 
                        (contacto_id, tipo, direccion, verificado, fecha_verificacion, preferido)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        contacto_id,
                        email.get('tipo'),
                        email.get('direccion'),
                        email.get('verificado'),
                        email.get('fecha_verificacion'),
                        email.get('preferido')
                    ))
                
                # Teléfonos
                for telefono in contacto.get('telefonos', []):
                    cursor.execute("""
                        INSERT INTO clientes_contacto_telefonos 
                        (contacto_id, tipo, numero, pais, operadora, activo, fecha_activacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        contacto_id,
                        telefono.get('tipo'),
                        telefono.get('numero'),
                        telefono.get('pais'),
                        telefono.get('operadora'),
                        telefono.get('activo'),
                        telefono.get('fecha_activacion')
                    ))
                
                # Redes sociales
                for red_social in contacto.get('redes_sociales', []):
                    cursor.execute("""
                        INSERT INTO clientes_contacto_redes_sociales 
                        (contacto_id, plataforma, usuario, url, seguidores, verificada)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        contacto_id,
                        red_social.get('plataforma'),
                        red_social.get('usuario'),
                        red_social.get('url'),
                        red_social.get('seguidores'),
                        red_social.get('verificada')
                    ))
            
            # Direcciones
            for direccion in cliente.get('direcciones', []):
                cursor.execute("""
                    INSERT INTO clientes_direcciones 
                    (cliente_id, tipo, calle, piso, codigo_postal, ciudad, provincia, pais, fecha_registro, activa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    cliente_id,
                    direccion.get('tipo'),
                    direccion.get('calle'),
                    direccion.get('piso'),
                    direccion.get('codigo_postal'),
                    direccion.get('ciudad'),
                    direccion.get('provincia'),
                    direccion.get('pais'),
                    direccion.get('fecha_registro'),
                    direccion.get('activa')
                ))
                direccion_id = cursor.lastrowid
                
                # Coordenadas
                coordenadas = direccion.get('coordenadas', {})
                if coordenadas:
                    cursor.execute("""
                        INSERT INTO clientes_direcciones_coordenadas 
                        (direccion_id, latitud, longitud)
                        VALUES (%s, %s, %s)
                    """, (
                        direccion_id,
                        coordenadas.get('latitud'),
                        coordenadas.get('longitud')
                    ))
            
            # Empleo
            empleo = cliente.get('empleo', {})
            if empleo:
                cursor.execute("INSERT INTO clientes_empleo (cliente_id) VALUES (%s)", (cliente_id,))
                empleo_id = cursor.lastrowid
                
                # Empresa actual
                empresa_actual = empleo.get('empresa_actual', {})
                if empresa_actual:
                    cursor.execute("""
                        INSERT INTO clientes_empleo_empresa_actual 
                        (empleo_id, nombre, cargo, departamento, fecha_inicio, salario_anual, moneda, tipo_contrato, jornada, edificio, calle, ciudad, codigo_postal)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        empleo_id,
                        empresa_actual.get('nombre'),
                        empresa_actual.get('cargo'),
                        empresa_actual.get('departamento'),
                        empresa_actual.get('fecha_inicio'),
                        empresa_actual.get('salario_anual'),
                        empresa_actual.get('moneda'),
                        empresa_actual.get('tipo_contrato'),
                        empresa_actual.get('jornada'),
                        empresa_actual.get('direccion_oficina', {}).get('edificio'),
                        empresa_actual.get('direccion_oficina', {}).get('calle'),
                        empresa_actual.get('direccion_oficina', {}).get('ciudad'),
                        empresa_actual.get('direccion_oficina', {}).get('codigo_postal')
                    ))
                    empresa_actual_id = cursor.lastrowid
                    
                    # Beneficios
                    for beneficio in empresa_actual.get('beneficios', []):
                        cursor.execute("""
                            INSERT INTO clientes_empleo_empresa_actual_beneficios 
                            (empresa_actual_id, beneficio)
                            VALUES (%s, %s)
                        """, (empresa_actual_id, beneficio))
                
                # Historial laboral
                for historial in empleo.get('historial_laboral', []):
                    cursor.execute("""
                        INSERT INTO clientes_empleo_historial_laboral 
                        (empleo_id, empresa, cargo, fecha_inicio, fecha_fin, motivo_salida)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        empleo_id,
                        historial.get('empresa'),
                        historial.get('cargo'),
                        historial.get('fecha_inicio'),
                        historial.get('fecha_fin'),
                        historial.get('motivo_salida')
                    ))
            
            # Educación
            educacion = cliente.get('educacion', {})
            if educacion:
                cursor.execute("INSERT INTO clientes_educacion (cliente_id, nivel_maximo) VALUES (%s, %s)", 
                              (cliente_id, educacion.get('nivel_maximo')))
                educacion_id = cursor.lastrowid
                
                # Estudios
                for estudio in educacion.get('estudios', []):
                    cursor.execute("""
                        INSERT INTO clientes_educacion_estudios 
                        (educacion_id, titulacion, institucion, fecha_inicio, fecha_fin, puntuacion, especialidad)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        educacion_id,
                        estudio.get('titulacion'),
                        estudio.get('institucion'),
                        estudio.get('fecha_inicio'),
                        estudio.get('fecha_fin'),
                        estudio.get('puntuacion'),
                        estudio.get('especialidad')
                    ))
                
                # Certificaciones
                for certificacion in educacion.get('certificaciones', []):
                    cursor.execute("""
                        INSERT INTO clientes_educacion_certificaciones 
                        (educacion_id, nombre, institucion, fecha_obtencion, fecha_expiracion, id_certificacion)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        educacion_id,
                        certificacion.get('nombre'),
                        certificacion.get('institucion'),
                        certificacion.get('fecha_obtencion'),
                        certificacion.get('fecha_expiracion'),
                        certificacion.get('id_certificacion')
                    ))
            
            # Preferencias
            preferencias = cliente.get('preferencias', {})
            if preferencias:
                cursor.execute("INSERT INTO clientes_preferencias (cliente_id) VALUES (%s)", (cliente_id,))
                preferencias_id = cursor.lastrowid
                
                # Comunicación
                comunicacion = preferencias.get('comunicacion', {})
                if comunicacion:
                    cursor.execute("""
                        INSERT INTO clientes_preferencias_comunicacion 
                        (preferencias_id, canal_preferido, frecuencia_newsletter, acepta_marketing, idioma, zona_horaria)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        preferencias_id,
                        comunicacion.get('canal_preferido'),
                        comunicacion.get('frecuencia_newsletter'),
                        comunicacion.get('acepta_marketing'),
                        comunicacion.get('idioma'),
                        comunicacion.get('zona_horaria')
                    ))
                
                # Productos de interés
                for producto in preferencias.get('productos_interes', []):
                    cursor.execute("""
                        INSERT INTO clientes_preferencias_productos_interes 
                        (preferencias_id, producto)
                        VALUES (%s, %s)
                    """, (preferencias_id, producto))
                
                # Categorías favoritas
                for categoria in preferencias.get('categorias_favoritas', []):
                    cursor.execute("""
                        INSERT INTO clientes_preferencias_categorias_favoritas 
                        (preferencias_id, categoria, nivel_interes, ultima_visita)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        preferencias_id,
                        categoria.get('categoria'),
                        categoria.get('nivel_interes'),
                        categoria.get('ultima_visita')
                    ))
            
            print(f"Cliente {cliente_id} insertado correctamente")
            
        except Exception as e:
            print(f"Error insertando cliente {cliente.get('id')}: {e}")
            continue

def main():
    # Cargar datos JSON
    json_data = load_json_data("clientes.json")
    
    if json_data is None:
        print("No se pudo cargar el archivo JSON. Creando datos de ejemplo...")
        # Aquí puedes poner tus datos JSON directamente
        json_data = {
            "clientes": [
                # Tus datos van aquí
            ]
        }
    
    # Crear tablas
    conn, cursor = create_tables_from_json(json_data)
    
    # Insertar datos
    print("\nInsertando datos en las tablas...")
    insert_json_data(cursor, json_data)
    
    # Hacer commit y cerrar conexión
    conn.commit()
    
    # Mostrar resumen
    print("\nResumen de la base de datos creada:")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Tabla {table_name}: {count} registros")
    
    cursor.close()
    conn.close()
    print("\nProceso completado exitosamente!")

if __name__ == "__main__":
    main()
    