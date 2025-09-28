from PIL import Image

img = Image.new("RGB" , size=(200,200), color ="white")

texto = open("texto.txt", 'r')
print(texto.readlines())
             
img.save("mensaje.png")
