from PIL import Image

img = Image.open("Laia.jpg")
tamanio = img.size
pixels = img.load()
for x in range(0, tamanio[0]):
    for y in range(0, tamanio[1]):
        pixel = img.getpixel((x,y))
        pixels[x, y]= (255-pixel[0],255-pixel[1], 255-pixel[2])
img.save("Laia2.jpg")      
