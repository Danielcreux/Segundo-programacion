#Primero escribimos un archivo 

archivo = open("clientes.txt",'W')

archivo.write("Esto es un texto")

archivo.close()

#Ahora vamos a leer archivos 

archivo = open("clientes.txt",'r')
lineas = archivo.readlines()
for linea in lineas:
    print(linea)
    
    
#Archivo aprendizamos en archivos 

archivo = open("clientes.txt",'a')

archivo.write("Esto es otro texto")

archivo.close()

#Ahora vamos a leer archivos 

archivo = open("clientes.txt",'r')
lineas = archivo.readlines()
for linea in lineas:
    print(linea)