import os

try:
    os.mkdir("secuenciales")
    
except:
    
    pass

for i in range(0,100):
    archivo = open("secuenciales/cliente"+str(i)+".json",'w')
    archivo.write("texto del cliente")
    archivo.close()

