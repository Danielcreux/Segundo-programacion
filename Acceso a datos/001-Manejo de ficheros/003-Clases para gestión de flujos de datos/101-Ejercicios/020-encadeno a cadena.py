from PIL import Image
import math 
import sys
import argparse 

parser = argparse.ArgumentParser(description="Convierte un texto en una imagen RGB")
parser.add_argument("-i", "--entrada", required=True, help="Texto de entrada")
args = parser.parse_args()


img = Image.open(args.entrada)
pixels = img.load()
tamanio = img.size
cadena = " "
for x in range (0, tamanio[0]):
          for y in range(0, tamanio[1]):
                    for dato in pixels[x,y]:
                               cadena += chr(dato)
print(cadena)
