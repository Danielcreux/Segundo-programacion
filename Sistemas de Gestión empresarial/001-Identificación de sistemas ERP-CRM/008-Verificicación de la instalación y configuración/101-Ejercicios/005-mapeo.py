import xml.etree.ElementTree as ET

def miInterfaz(destino):
      cadena = ""
      # Parse the XML file
    tree = ET.parse()
    root = tree.getroot(destino)

      # Print the root element
    print("Root element:", root.tag)

      # Iterate over each child element
    for campo in root:
          print(f"Etiqueta: {campo.tag}, atributo nombre: {campo.get('nombre')}")
        if campo.tag == "campotexto":
            cadena += "<input type='text' name='"+campo.get('nombre')+"'>"
        elif campo.tag == "areadetexto":
            cadena += "<textarea name='"+campo.get('nombre')+"'></textarea>"
return cadena
      
