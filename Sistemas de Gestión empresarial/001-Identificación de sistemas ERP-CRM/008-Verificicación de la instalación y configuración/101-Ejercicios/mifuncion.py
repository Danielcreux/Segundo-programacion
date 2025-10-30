import xml.etree.ElementTree as ET
import sqlite3


def miInterfaz(destino):
    conexion = sqlite3.connect("odoo.db")
    cursor = conexion.cursor()
    cadena = ""
    peticion = '''
      CREATE TABLE IF NOT EXISTS "interfaz" (
        "Identificador"	INTEGER,
        '''


    # Parse the XML file
    tree = ET.parse(destino)
    root = tree.getroot()

    # Print the root element
    print("Root element:", root.tag)

    # Iterate over each child element
    for campo in root:
    print(f"Etiqueta: {campo.tag}, atributo nombre: {campo.get('nombre')}")
    if campo.tag == "campotexto":
        cadena += "<input type='text' name='"+campo.get('nombre')+"' placeholder='"+campo.get('nombre')+"'>"
    elif campo.tag == "areadetexto":
        cadena += "<textarea name='"+campo.get('nombre')+"'></textarea>"
    peticion += '"'+campo.get('nombre')+'"	TEXT,'   

    peticion += '''

        PRIMARY KEY("Identificador" AUTOINCREMENT)
    );
    ''' 
    #print(peticion)
    cursor.execute(peticion)
    conexion.commit()

return cadena
      
