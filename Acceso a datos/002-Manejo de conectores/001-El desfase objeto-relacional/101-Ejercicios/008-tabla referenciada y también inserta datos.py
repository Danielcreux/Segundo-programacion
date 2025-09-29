import mysql.connector

clientes = [{
    "nombre": "Joshue Daniel",
    "apellidos": "Freire Sanchez",
    "dni": "60839687H",
    "edad": 25,
    "emails": [
        {
            "tipo": "personal",
            "direccion": "info@joshue.com",
        },
        {
            "tipo": "empresa",
            "direccion": "info@danielcreux.com"
        }
    ]
}, {
    "nombre": "Joshue Daniel",
    "apellidos": "Freire Sanchez",
    "dni": "60839687H",
    "edad": 25,
    "emails": [
        {
            "tipo": "personal",
            "direccion": "info@joshue.com",
        },
        {
            "tipo": "empresa",
            "direccion": "info@danielcreux.com"
        }
    ]
}]

muestra = clientes[0]
print(muestra)

campos = []
tablas_externas = []

for clave in muestra.keys():
    print(clave)
    print(type(muestra[clave]))
    if type(muestra[clave]) == str:
        print("Lo voy a convertir en una columna de SQL que será de tipo varchar")
        campos.append((clave, 'varchar'))
    elif type(muestra[clave]) == list:
        print("Lo voy a convertir en una tabla externa de SQL")
        tablas_externas.append(clave)
    elif type(muestra[clave]) == int:
        print("Lo voy a convertir en una columna de SQL que será de tipo int")
        campos.append((clave, 'int'))
    else:
        print("No hay ninguna conversión por realizar")

conn = mysql.connector.connect(
    host="localhost",
    user="desfase",
    password="desfase",
    database="desfase"
)

cursor = conn.cursor()

# Drop existing tables in correct order (child tables first)
cursor.execute("DROP TABLE IF EXISTS clientes_emails")
cursor.execute("DROP TABLE IF EXISTS clientes")

# Create main clientes table
cadena = '''
    CREATE TABLE `clientes` (
    `identificador` INT NOT NULL AUTO_INCREMENT,
'''

for campo, tipo in campos:
    if tipo == 'varchar':
        cadena += f'''    `{campo}` VARCHAR(255) NOT NULL,
'''
    elif tipo == 'int':
        cadena += f'''    `{campo}` INT NOT NULL,
'''

cadena += '''
    PRIMARY KEY (`identificador`)
) ENGINE = InnoDB;
'''

print("=== CREATING MAIN TABLE ===")
print(cadena)
cursor.execute(cadena)

# Create external tables for array properties
for tabla_externa in tablas_externas:
    if tabla_externa == 'emails':
        # Create emails table
        cadena_emails = '''
        CREATE TABLE `clientes_emails` (
            `email_id` INT NOT NULL AUTO_INCREMENT,
            `cliente_id` INT NOT NULL,
            `tipo` VARCHAR(50) NOT NULL,
            `direccion` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`email_id`),
            FOREIGN KEY (`cliente_id`) REFERENCES `clientes`(`identificador`) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        '''
        print(f"=== CREATING EXTERNAL TABLE: {tabla_externa} ===")
        print(cadena_emails)
        cursor.execute(cadena_emails)

# Insert sample data
print("=== INSERTING SAMPLE DATA ===")

# Insert clients
for i, cliente in enumerate(clientes):
    # Build INSERT statement for main client data
    column_names = []
    placeholders = []
    values = []
    
    for campo, tipo in campos:
        column_names.append(campo)
        placeholders.append("%s")
        values.append(cliente[campo])
    
    insert_client = f'''
    INSERT INTO clientes ({', '.join(column_names)})
    VALUES ({', '.join(placeholders)})
    '''
    
    cursor.execute(insert_client, values)
    client_id = cursor.lastrowid
    
    print(f"Inserted client with ID: {client_id}")
    
    # Insert emails if they exist
    if 'emails' in cliente and cliente['emails']:
        for email in cliente['emails']:
            insert_email = '''
            INSERT INTO clientes_emails (cliente_id, tipo, direccion)
            VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_email, (client_id, email['tipo'], email['direccion']))
            print(f"Inserted email for client {client_id}: {email['direccion']}")

# Commit changes
conn.commit()

# Verify data by querying
print("\n=== VERIFYING DATA ===")

# Query clients
cursor.execute("SELECT * FROM clientes")
clientes_db = cursor.fetchall()
print("Clients table:")
for cliente in clientes_db:
    print(cliente)

# Query emails
cursor.execute("""
SELECT ce.email_id, ce.cliente_id, ce.tipo, ce.direccion, c.nombre, c.apellidos 
FROM clientes_emails ce 
JOIN clientes c ON ce.cliente_id = c.identificador
""")
emails_db = cursor.fetchall()
print("\nEmails table (with client info):")
for email in emails_db:
    print(email)

cursor.close()
conn.close()