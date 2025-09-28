from PIL import Image

img = Image.new("RGB" , size=(200,200), color ="white")

texto = open("texto.txt", 'r')
lineas = texto.readlines()
letras = []
for linea in lineas:
          for letra in linea:
            letras.append(letra)

print(letras)
             
img.save("mensaje.png")
