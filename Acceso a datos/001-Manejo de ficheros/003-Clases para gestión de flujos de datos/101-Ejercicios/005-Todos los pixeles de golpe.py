from PIL import Image

img = Image.open("italia.jpg")
tamanio = img.size
pixel = img.getpixel((0,0))

print(pixel)       
