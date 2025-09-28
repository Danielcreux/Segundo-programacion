from PIL import Image
import math 
import sys
import argparse 

parser = argparse.ArgumentParser(description="Convierte un texto en una imagen RGB")
parser.add_argument("-i", "--entrada", required=True, help="Texto de entrada")
parser.add_argument("-o", "--salida", required=True, help="Archivo de salida (ej:salida.png)")
args = parser.parse_args()

# Cargo el texto
texto = args.entrada
letras = list(texto)

# Calculate image dimensions
longitudtexto = len(letras) / 3
raizcuadrada = math.sqrt(longitudtexto)
techo = math.ceil(raizcuadrada)

# Make sure we have enough pixels
total_pixels_needed = math.ceil(len(letras) / 3)
if techo * techo < total_pixels_needed:
    techo += 1

print(f"La longitud del texto es de: {len(texto)}")
print(f"La raiz cuadrada es de: {raizcuadrada}")
print(f"Redondeo al alza: {techo}")

img = Image.new("RGB", size=(techo, techo), color="white")
pixels = img.load()

# Pad the text to be divisible by 3
while len(letras) % 3 != 0:
    letras.append('\0')  # Null character as padding

contador = 0
for i in range(0, len(letras), 3):
    x = contador % techo
    y = contador // techo
    pixels[x, y] = (ord(letras[i]), ord(letras[i+1]), ord(letras[i+2]))
    contador += 1

img.save(args.salida)
print(f"Imagen guardada como {args.salida}")