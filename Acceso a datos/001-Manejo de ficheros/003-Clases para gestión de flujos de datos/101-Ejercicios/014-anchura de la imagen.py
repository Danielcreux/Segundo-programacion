from PIL import Image
import math 

img = Image.new("RGB" , size=(200,200), color ="white")
pixels = img.load()

texto = open("texto.txt", 'r')
lineas = texto.readlines()
letras = []
for linea in lineas:
          for letra in linea:
            letras.append(letra)
contador = 0
for i in range(0,len(letras),3):
          try:
                    print("r:",letras[i], ord(letras[i]))
                    print("g:",letras[i+1], ord(letras[i+1]))
                    print("b:",letras[i+2], ord(letras[i+2]))
                    pixels[(i/3)%200,math.floor(i/3)/200] = ord(letras[i]) , ord(letras[i+1]) , ord(letras[i+2])
                    print("siguiente pixel")
          except:
                    pass
          
             
img.save("mensaje.png")
