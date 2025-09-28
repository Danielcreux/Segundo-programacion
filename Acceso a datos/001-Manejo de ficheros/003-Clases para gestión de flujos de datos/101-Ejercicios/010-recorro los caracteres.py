from PIL import Image

img = Image.new("RGB" , size=(200,200), color ="white")

texto = open("texto.txt", 'r')
lineas = texto.readlines()
for linea in lineas:
          for letra in linea:
             print(letra)
             
img.save("mensaje.png")
