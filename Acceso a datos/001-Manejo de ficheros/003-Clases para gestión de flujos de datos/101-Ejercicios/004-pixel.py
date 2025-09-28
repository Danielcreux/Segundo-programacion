from PIL import Image

img = Image.open("italia.jpg")

pixel = img.getpixel((0,0))

print(pixel)       
