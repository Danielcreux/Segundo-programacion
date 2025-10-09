import mysql.connector
import json
from typing import Dict, List, Any

def get_database_connection():
    """Establecer conexión con la base de datos"""
    return mysql.connector.connect(
        host="localhost",
        user="desfase",
        password="desfase",
        database="desfase"
    )

def get_all_tables(cursor):
    """Obtener todas las tablas de la base de datos"""
    cursor.execute("SHOW TABLES")
    return [table[0] for table in cursor.fetchall()]

def reconstruct_clientes_structure(cursor):
    """Reconstruir la estructura completa de clientes desde la base de datos"""
    
    # Obtener todos los clientes principales
    cursor.execute("SELECT * FROM clientes")
    clientes_data = cursor.fetchall()
    clientes_columns = [desc[0] for desc in cursor.description]
    
    clientes_dict = {"clientes": []}
    
    for cliente_row in clientes_data:
        cliente_dict = {}
        
        # Convertir fila a diccionario
        for i, column in enumerate(clientes_columns):
            if column != 'id':  # No incluir el id autoincremental
                cliente_dict[column] = cliente_row[i]
        
        cliente_id = cliente_dict['cliente_id']
        
        # Reconstruir información personal
        cliente_dict['informacion_personal'] = reconstruct_informacion_personal(cursor, cliente_id)
        
        # Reconstruir contacto
        cliente_dict['contacto'] = reconstruct_contacto(cursor, cliente_id)
        
        # Reconstruir direcciones
        cliente_dict['direcciones'] = reconstruct_direcciones(cursor, cliente_id)
        
        # Reconstruir empleo
        cliente_dict['empleo'] = reconstruct_empleo(cursor, cliente_id)
        
        # Reconstruir educación
        cliente_dict['educacion'] = reconstruct_educacion(cursor, cliente_id)
        
        # Reconstruir preferencias
        cliente_dict['preferencias'] = reconstruct_preferencias(cursor, cliente_id)
        
        # Reconstruir metadatos
        cliente_dict['metadatos'] = reconstruct_metadatos(cliente_dict)
        
        # Limpiar campos de metadatos del nivel principal
        fields_to_remove = ['fecha_registro', 'fecha_ultima_actualizacion', 'estado', 'puntuacion_riesgo', 'segmento']
        for field in fields_to_remove:
            if field in cliente_dict:
                del cliente_dict[field]
        
        clientes_dict["clientes"].append(cliente_dict)
    
    return clientes_dict

def reconstruct_informacion_personal(cursor, cliente_id):
    """Reconstruir información personal"""
    cursor.execute("""
        SELECT nombre, apellidos, dni, edad, fecha_nacimiento, genero, nacionalidad 
        FROM clientes_informacion_personal 
        WHERE cliente_id = %s
    """, (cliente_id,))
    
    result = cursor.fetchone()
    if result:
        columns = ['nombre', 'apellidos', 'dni', 'edad', 'fecha_nacimiento', 'genero', 'nacionalidad']
        return {columns[i]: result[i] for i in range(len(columns))}
    return {}

def reconstruct_contacto(cursor, cliente_id):
    """Reconstruir información de contacto"""
    contacto_dict = {}
    
    # Obtener el ID de contacto
    cursor.execute("SELECT id FROM clientes_contacto WHERE cliente_id = %s", (cliente_id,))
    contacto_result = cursor.fetchone()
    
    if contacto_result:
        contacto_id = contacto_result[0]
        
        # Reconstruir emails
        contacto_dict['emails'] = reconstruct_emails(cursor, contacto_id)
        
        # Reconstruir teléfonos
        contacto_dict['telefonos'] = reconstruct_telefonos(cursor, contacto_id)
        
        # Reconstruir redes sociales
        contacto_dict['redes_sociales'] = reconstruct_redes_sociales(cursor, contacto_id)
    
    return contacto_dict

def reconstruct_emails(cursor, contacto_id):
    """Reconstruir lista de emails"""
    cursor.execute("""
        SELECT tipo, direccion, verificado, fecha_verificacion, preferido 
        FROM clientes_contacto_emails 
        WHERE contacto_id = %s
    """, (contacto_id,))
    
    emails = []
    columns = ['tipo', 'direccion', 'verificado', 'fecha_verificacion', 'preferido']
    
    for row in cursor.fetchall():
        email_dict = {}
        for i, column in enumerate(columns):
            email_dict[column] = row[i]
        emails.append(email_dict)
    
    return emails

def reconstruct_telefonos(cursor, contacto_id):
    """Reconstruir lista de teléfonos"""
    cursor.execute("""
        SELECT tipo, numero, pais, operadora, activo, fecha_activacion 
        FROM clientes_contacto_telefonos 
        WHERE contacto_id = %s
    """, (contacto_id,))
    
    telefonos = []
    columns = ['tipo', 'numero', 'pais', 'operadora', 'activo', 'fecha_activacion']
    
    for row in cursor.fetchall():
        telefono_dict = {}
        for i, column in enumerate(columns):
            telefono_dict[column] = row[i]
        telefonos.append(telefono_dict)
    
    return telefonos

def reconstruct_redes_sociales(cursor, contacto_id):
    """Reconstruir lista de redes sociales"""
    cursor.execute("""
        SELECT plataforma, usuario, url, seguidores, verificada 
        FROM clientes_contacto_redes_sociales 
        WHERE contacto_id = %s
    """, (contacto_id,))
    
    redes_sociales = []
    columns = ['plataforma', 'usuario', 'url', 'seguidores', 'verificada']
    
    for row in cursor.fetchall():
        red_social_dict = {}
        for i, column in enumerate(columns):
            red_social_dict[column] = row[i]
        redes_sociales.append(red_social_dict)
    
    return redes_sociales

def reconstruct_direcciones(cursor, cliente_id):
    """Reconstruir lista de direcciones"""
    cursor.execute("""
        SELECT id, tipo, calle, piso, codigo_postal, ciudad, provincia, pais, fecha_registro, activa 
        FROM clientes_direcciones 
        WHERE cliente_id = %s
    """, (cliente_id,))
    
    direcciones = []
    columns = ['id', 'tipo', 'calle', 'piso', 'codigo_postal', 'ciudad', 'provincia', 'pais', 'fecha_registro', 'activa']
    
    for row in cursor.fetchall():
        direccion_dict = {}
        for i, column in enumerate(columns):
            if column != 'id':  # No incluir el ID interno
                direccion_dict[column] = row[i]
        
        # Reconstruir coordenadas
        direccion_id = row[0]  # El ID está en la primera posición
        coordenadas = reconstruct_coordenadas(cursor, direccion_id)
        if coordenadas:
            direccion_dict['coordenadas'] = coordenadas
        
        direcciones.append(direccion_dict)
    
    return direcciones

def reconstruct_coordenadas(cursor, direccion_id):
    """Reconstruir coordenadas de una dirección"""
    cursor.execute("""
        SELECT latitud, longitud 
        FROM clientes_direcciones_coordenadas 
        WHERE direccion_id = %s
    """, (direccion_id,))
    
    result = cursor.fetchone()
    if result:
        return {'latitud': float(result[0]), 'longitud': float(result[1])}
    return {}

def reconstruct_empleo(cursor, cliente_id):
    """Reconstruir información de empleo"""
    empleo_dict = {}
    
    # Obtener el ID de empleo
    cursor.execute("SELECT id FROM clientes_empleo WHERE cliente_id = %s", (cliente_id,))
    empleo_result = cursor.fetchone()
    
    if empleo_result:
        empleo_id = empleo_result[0]
        
        # Reconstruir empresa actual
        empleo_dict['empresa_actual'] = reconstruct_empresa_actual(cursor, empleo_id)
        
        # Reconstruir historial laboral
        empleo_dict['historial_laboral'] = reconstruct_historial_laboral(cursor, empleo_id)
    
    return empleo_dict

def reconstruct_empresa_actual(cursor, empleo_id):
    """Reconstruir información de empresa actual"""
    cursor.execute("""
        SELECT nombre, cargo, departamento, fecha_inicio, salario_anual, moneda, 
               tipo_contrato, jornada, edificio, calle, ciudad, codigo_postal 
        FROM clientes_empleo_empresa_actual 
        WHERE empleo_id = %s
    """, (empleo_id,))
    
    result = cursor.fetchone()
    if result:
        columns = ['nombre', 'cargo', 'departamento', 'fecha_inicio', 'salario_anual', 'moneda', 
                  'tipo_contrato', 'jornada', 'edificio', 'calle', 'ciudad', 'codigo_postal']
        
        empresa_dict = {columns[i]: result[i] for i in range(len(columns))}
        
        # Reconstruir dirección de oficina
        direccion_oficina = {}
        if result[8]:  # edificio
            direccion_oficina['edificio'] = result[8]
        if result[9]:  # calle
            direccion_oficina['calle'] = result[9]
        if result[10]:  # ciudad
            direccion_oficina['ciudad'] = result[10]
        if result[11]:  # codigo_postal
            direccion_oficina['codigo_postal'] = result[11]
        
        if direccion_oficina:
            empresa_dict['direccion_oficina'] = direccion_oficina
        
        # Limpiar campos individuales de dirección
        for field in ['edificio', 'calle', 'ciudad', 'codigo_postal']:
            if field in empresa_dict:
                del empresa_dict[field]
        
        # Reconstruir beneficios
        empresa_dict['beneficios'] = reconstruct_beneficios(cursor, empleo_id)
        
        return empresa_dict
    return {}

def reconstruct_beneficios(cursor, empleo_id):
    """Reconstruir lista de beneficios"""
    # Primero obtener el ID de empresa actual
    cursor.execute("SELECT id FROM clientes_empleo_empresa_actual WHERE empleo_id = %s", (empleo_id,))
    empresa_result = cursor.fetchone()
    
    if empresa_result:
        empresa_actual_id = empresa_result[0]
        cursor.execute("SELECT beneficio FROM clientes_empleo_empresa_actual_beneficios WHERE empresa_actual_id = %s", 
                      (empresa_actual_id,))
        
        return [row[0] for row in cursor.fetchall()]
    
    return []

def reconstruct_historial_laboral(cursor, empleo_id):
    """Reconstruir historial laboral"""
    cursor.execute("""
        SELECT empresa, cargo, fecha_inicio, fecha_fin, motivo_salida 
        FROM clientes_empleo_historial_laboral 
        WHERE empleo_id = %s
    """, (empleo_id,))
    
    historial = []
    columns = ['empresa', 'cargo', 'fecha_inicio', 'fecha_fin', 'motivo_salida']
    
    for row in cursor.fetchall():
        historial_dict = {}
        for i, column in enumerate(columns):
            historial_dict[column] = row[i]
        historial.append(historial_dict)
    
    return historial

def reconstruct_educacion(cursor, cliente_id):
    """Reconstruir información de educación"""
    educacion_dict = {}
    
    # Obtener información básica de educación
    cursor.execute("SELECT nivel_maximo FROM clientes_educacion WHERE cliente_id = %s", (cliente_id,))
    educacion_result = cursor.fetchone()
    
    if educacion_result:
        educacion_dict['nivel_maximo'] = educacion_result[0]
        
        # Obtener ID de educación
        cursor.execute("SELECT id FROM clientes_educacion WHERE cliente_id = %s", (cliente_id,))
        educacion_id_result = cursor.fetchone()
        
        if educacion_id_result:
            educacion_id = educacion_id_result[0]
            
            # Reconstruir estudios
            educacion_dict['estudios'] = reconstruct_estudios(cursor, educacion_id)
            
            # Reconstruir certificaciones
            educacion_dict['certificaciones'] = reconstruct_certificaciones(cursor, educacion_id)
    
    return educacion_dict

def reconstruct_estudios(cursor, educacion_id):
    """Reconstruir lista de estudios"""
    cursor.execute("""
        SELECT titulacion, institucion, fecha_inicio, fecha_fin, puntuacion, especialidad 
        FROM clientes_educacion_estudios 
        WHERE educacion_id = %s
    """, (educacion_id,))
    
    estudios = []
    columns = ['titulacion', 'institucion', 'fecha_inicio', 'fecha_fin', 'puntuacion', 'especialidad']
    
    for row in cursor.fetchall():
        estudio_dict = {}
        for i, column in enumerate(columns):
            estudio_dict[column] = row[i]
        estudios.append(estudio_dict)
    
    return estudios

def reconstruct_certificaciones(cursor, educacion_id):
    """Reconstruir lista de certificaciones"""
    cursor.execute("""
        SELECT nombre, institucion, fecha_obtencion, fecha_expiracion, id_certificacion 
        FROM clientes_educacion_certificaciones 
        WHERE educacion_id = %s
    """, (educacion_id,))
    
    certificaciones = []
    columns = ['nombre', 'institucion', 'fecha_obtencion', 'fecha_expiracion', 'id_certificacion']
    
    for row in cursor.fetchall():
        certificacion_dict = {}
        for i, column in enumerate(columns):
            certificacion_dict[column] = row[i]
        certificaciones.append(certificacion_dict)
    
    return certificaciones

def reconstruct_preferencias(cursor, cliente_id):
    """Reconstruir información de preferencias"""
    preferencias_dict = {}
    
    # Obtener el ID de preferencias
    cursor.execute("SELECT id FROM clientes_preferencias WHERE cliente_id = %s", (cliente_id,))
    preferencias_result = cursor.fetchone()
    
    if preferencias_result:
        preferencias_id = preferencias_result[0]
        
        # Reconstruir comunicación
        preferencias_dict['comunicacion'] = reconstruct_comunicacion(cursor, preferencias_id)
        
        # Reconstruir productos de interés
        preferencias_dict['productos_interes'] = reconstruct_productos_interes(cursor, preferencias_id)
        
        # Reconstruir categorías favoritas
        preferencias_dict['categorias_favoritas'] = reconstruct_categorias_favoritas(cursor, preferencias_id)
    
    return preferencias_dict

def reconstruct_comunicacion(cursor, preferencias_id):
    """Reconstruir preferencias de comunicación"""
    cursor.execute("""
        SELECT canal_preferido, frecuencia_newsletter, acepta_marketing, idioma, zona_horaria 
        FROM clientes_preferencias_comunicacion 
        WHERE preferencias_id = %s
    """, (preferencias_id,))
    
    result = cursor.fetchone()
    if result:
        columns = ['canal_preferido', 'frecuencia_newsletter', 'acepta_marketing', 'idioma', 'zona_horaria']
        return {columns[i]: result[i] for i in range(len(columns))}
    return {}

def reconstruct_productos_interes(cursor, preferencias_id):
    """Reconstruir lista de productos de interés"""
    cursor.execute("SELECT producto FROM clientes_preferencias_productos_interes WHERE preferencias_id = %s", 
                  (preferencias_id,))
    
    return [row[0] for row in cursor.fetchall()]

def reconstruct_categorias_favoritas(cursor, preferencias_id):
    """Reconstruir lista de categorías favoritas"""
    cursor.execute("""
        SELECT categoria, nivel_interes, ultima_visita 
        FROM clientes_preferencias_categorias_favoritas 
        WHERE preferencias_id = %s
    """, (preferencias_id,))
    
    categorias = []
    columns = ['categoria', 'nivel_interes', 'ultima_visita']
    
    for row in cursor.fetchall():
        categoria_dict = {}
        for i, column in enumerate(columns):
            categoria_dict[column] = row[i]
        categorias.append(categoria_dict)
    
    return categorias

def reconstruct_metadatos(cliente_dict):
    """Reconstruir metadatos desde los campos del cliente principal"""
    return {
        'fecha_registro': cliente_dict.get('fecha_registro'),
        'fecha_ultima_actualizacion': cliente_dict.get('fecha_ultima_actualizacion'),
        'estado': cliente_dict.get('estado'),
        'puntuacion_riesgo': cliente_dict.get('puntuacion_riesgo'),
        'segmento': cliente_dict.get('segmento')
    }

def save_to_json(data: Dict, filename: str):
    """Guardar datos como archivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"Datos guardados en {filename}")

def main():
    """Función principal"""
    try:
        # Conectar a la base de datos
        conn = get_database_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("Conectado a la base de datos. Reconstruyendo estructura...")
        
        # 1. Reconstruir como diccionario Python
        print("Reconstruyendo datos como diccionario Python...")
        clientes_dict = reconstruct_clientes_structure(cursor)
        
        # 2. Mostrar información del diccionario
        print(f"\nDiccionario Python reconstruido:")
        print(f"Número de clientes: {len(clientes_dict['clientes'])}")
        
        if clientes_dict['clientes']:
            primer_cliente = clientes_dict['clientes'][0]
            print(f"Primer cliente: {primer_cliente.get('id', 'N/A')} - {primer_cliente.get('informacion_personal', {}).get('nombre', 'N/A')}")
            
            # Mostrar estructura del primer cliente
            print("\nEstructura del primer cliente:")
            for key in primer_cliente.keys():
                if isinstance(primer_cliente[key], dict):
                    print(f"  {key}: dict con {len(primer_cliente[key])} campos")
                elif isinstance(primer_cliente[key], list):
                    print(f"  {key}: lista con {len(primer_cliente[key])} elementos")
                else:
                    print(f"  {key}: {type(primer_cliente[key]).__name__}")
        
        # 3. Guardar como JSON
        json_filename = "clientes_reconstruidos.json"
        save_to_json(clientes_dict, json_filename)
        
        # 4. Mostrar resumen de tablas procesadas
        tables = get_all_tables(cursor)
        print(f"\nTablas procesadas: {len(tables)}")
        for table in sorted(tables):
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"  {table}: {count} registros")
        
        print(f"\nProceso completado exitosamente!")
        print(f"1. Diccionario Python disponible en variable 'clientes_dict'")
        print(f"2. JSON guardado en '{json_filename}'")
        
        return clientes_dict
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

# Función adicional para mostrar datos específicos
def show_detailed_info(clientes_dict, cliente_id=None):
    """Mostrar información detallada de los clientes reconstruidos"""
    if not clientes_dict or 'clientes' not in clientes_dict:
        print("No hay datos para mostrar")
        return
    
    clientes = clientes_dict['clientes']
    print(f"\n{'='*60}")
    print(f"INFORMACIÓN DETALLADA DE CLIENTES RECONSTRUIDOS")
    print(f"{'='*60}")
    
    if cliente_id:
        # Mostrar cliente específico
        cliente = next((c for c in clientes if c.get('id') == cliente_id), None)
        if cliente:
            print(f"Cliente: {cliente_id}")
            print(json.dumps(cliente, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"Cliente {cliente_id} no encontrado")
    else:
        # Mostrar resumen de todos los clientes
        for i, cliente in enumerate(clientes):
            print(f"\nCliente {i+1}: {cliente.get('id', 'N/A')}")
            info_personal = cliente.get('informacion_personal', {})
            print(f"  Nombre: {info_personal.get('nombre', 'N/A')} {info_personal.get('apellidos', 'N/A')}")
            print(f"  Email: {len(cliente.get('contacto', {}).get('emails', []))} emails")
            print(f"  Direcciones: {len(cliente.get('direcciones', []))} direcciones")
            print(f"  Estado: {cliente.get('metadatos', {}).get('estado', 'N/A')}")

if __name__ == "__main__":
    # Ejecutar la reconstrucción
    reconstructed_data = main()
    
    # Mostrar información detallada si hay datos
    if reconstructed_data:
        show_detailed_info(reconstructed_data)
        
        # También puedes acceder a los datos individualmente
        # reconstructed_data['clientes'][0] - primer cliente
        # reconstructed_data['clientes'][0]['informacion_personal']['nombre'] - nombre del primer cliente