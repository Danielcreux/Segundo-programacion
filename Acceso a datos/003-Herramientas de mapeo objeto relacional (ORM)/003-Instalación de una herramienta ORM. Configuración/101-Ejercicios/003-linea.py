from PIL import Image, ImageDraw

# Crear imagen en blanco
img = Image.new("RGB", (800, 200), "white")

# Crear objeto de dibujo
draw = ImageDraw.Draw(img)

# Dibujar una línea (x1, y1, x2, y2)
draw.line((50, 100, 750, 100), fill="black", width=3)

# Guardar archivo
img.save("linea.png")

print("Imagen generada: linea.png")
