from PIL import Image
import math 
import sys

# Cargo el texto
texto = sys.argv[1]
letras = []
for letra in texto:
          letras.append(letra)
          
longitudtexto = len(letras)/3
print("La longitud del texto es de:", longitudtexto)
raizcuadrada = math.sqrt(longitudtexto)
print("La raiz cuadrada es de:",raizcuadrada)
techo = math.ceil(raizcuadrada)
print("Redondeo al alza:", techo)      


img = Image.new("RGB" , size=(techo,techo), color ="white")
pixels = img.load()

contador = 0
for i in range(0,len(letras),3):
          try:
                    pixels[(i/3)%techo,math.floor(i/3)/techo] = ord(letras[i]) , ord(letras[i+1]) , ord(letras[i+2])
          except:
                    pass         
img.save(sys.argv[2])
