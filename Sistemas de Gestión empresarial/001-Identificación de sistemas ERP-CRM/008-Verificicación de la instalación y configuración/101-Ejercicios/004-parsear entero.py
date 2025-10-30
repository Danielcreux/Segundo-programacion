import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('interfaz.xml')
root = tree.getroot()

# Print the root element
print("Root element:", root.tag)

# Iterate over each child element
for campo in root:
    print(f"Etiqueta: {campo.tag}, atributo nombre: {campo.get('nombre')}")
