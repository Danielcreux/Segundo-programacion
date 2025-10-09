archivo = open("clientes.csv",'r')

linea = archivo.readline()
tupla = linea.split(",")
print(tupla)
print(type(tupla))
archivo.close()