from PIL import Image

img = Image.open("italia.jpg")
pixels = img. load()
pixels[0, 0] = (0,0,0)

img.save("italia2.png")