from PIL import Image
import math 
import sys
import argparse 

parser = argparse.ArgumentParser(description="Convierte una imagen RGB en texto")
parser.add_argument("-i", "--entrada", required=True, help="Imagen de entrada")
args = parser.parse_args()

img = Image.open(args.entrada)
pixels = img.load()
tamanio = img.size
cadena = ""

for y in range(0, tamanio[1]):
    for x in range(0, tamanio[0]):
        r, g, b = pixels[x, y]
        # Only add characters that are printable (avoid null bytes and control characters)
        if r > 0 and r < 127:  # Printable ASCII range
            cadena += chr(r)
        if g > 0 and g < 127:
            cadena += chr(g)
        if b > 0 and b < 127:
            cadena += chr(b)

# Remove trailing null characters
cadena = cadena.rstrip('\0')
print(cadena)