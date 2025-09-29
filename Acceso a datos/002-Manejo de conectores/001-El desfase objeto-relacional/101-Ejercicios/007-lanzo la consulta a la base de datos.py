import mysql.connector

clientes =[{
    "nombre":"Joshue Daniel",
    "apellidos":"Freire Sanchez",
    "dni":"60839687H",
    "edad":25,
    "emails":[
        {
            "tipo":"personal",
            "direcciones":[
                "info@joshue.com",
                "joshue@gmail.com"
            ]
        },
        {
             "tipo":"empresa",
            "direcciones":[
                "info@danielcreux.com"
            ]
        }
    ]
},{
    "nombre":"Joshue Daniel",
    "apellidos":"Freire Sanchez",
    "dni":"60839687H",
    "edad":25,
    "emails":[
        {
            "tipo":"personal",
            "direcciones":[
                "info@joshue.com",
                "joshue@gmail.com"
            ]
        },
        {
             "tipo":"empresa",
            "direcciones":[
                "info@danielcreux.com"
            ]
        }
    ]
}
]

muestra = clientes[0]
print(muestra)

campos = []

for clave in muestra.keys():
    print(clave)
    print(type(muestra[clave]))
    if type(muestra[clave]) == str:
        print("Lo voy a convertir en una columna de SQL que será de tipo varchar")
        campos.append(clave)
    elif type(muestra[clave]) == list:
        print("Lo voy a convertir en una externa de SQL")
    elif type(muestra[clave]) == int:
        print("Lo voy a convertir en una columna de SQL que será de tipo int")
        campos.append(clave)
    else:
        print("No hay ninguna conversión por realizar")
    
conn = mysql.connector.connect(
    host = "localhost",
    user = "desfase",
    password = "desfase",
    database = "desfase" 
)

cadena = '''
    CREATE TABLE `desfase`.`clientes` (
    `Identificador` INT(255) NOT NULL AUTO_INCREMENT , 
    '''

for campo in campos:
    if type(campo) is str:
        cadena += '''
        `'''+campo+'''` VARCHAR(255) NOT NULL ,
        '''
    elif type(campo) is int:
        cadena += '''
        `'''+campo+'''` INT(255) NOT NULL ,
        '''

cadena += '''
    
     PRIMARY KEY (`Identificador`)
     ) ENGINE = InnoDB;
'''

print(cadena)
cursor = conn.cursor()
cursor.execute("DROP TABLE clientes")
cursor.execute(cadena)
    
    