from PIL import Image

img = Image.new("RGB" , size=(200,200), color ="white")

texto = open("texto.txt", 'r')
lineas = texto.readlines()
letras = []
for linea in lineas:
          for letra in linea:
            letras.append(letra)
contador = 0
for i in range(0,len(letras),3):
          try:
                    print("r:",letras[i])
                    print("g:",letras[i+1])
                    print("b:",letras[i+2])
                    print("siguiente pixel")
          except:
                    pass
          
             
img.save("mensaje.png")
