from lxml import etree

tree = etree.parse('interfaz.xml')
root = tree.getroot()

print(root)
