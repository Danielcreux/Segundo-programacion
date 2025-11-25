from PIL import Image, ImageDraw
from pydub import AudioSegment
import numpy as np

# --- Parámetros de la imagen ---
anchura = 800
altura = 200
color_fondo = "white"
color_trazo = "black"
grosor = 6              # grosor de cada "barra" (cápsula)
radio = grosor // 2     # radio de las puntas redondeadas

# --- Carga del audio ---
audio = AudioSegment.from_mp3("0802.mp3")

# Aseguramos mono para que no se mezclen canales L/R intercalados
if audio.channels > 1:
    muestras = np.array(audio.get_array_of_samples()).reshape((-1, audio.channels))
    muestras = muestras.mean(axis=1)
else:
    muestras = np.array(audio.get_array_of_samples())

numerosamples = len(muestras)

# --- Creación de la imagen ---
img = Image.new("RGB", (anchura, altura), color_fondo)
draw = ImageDraw.Draw(img)

# Relación índice de muestra → X en la imagen
paso_x = anchura / numerosamples

# Normalización de la amplitud
max_val = np.max(np.abs(muestras))
if max_val == 0:
    max_val = 1

centro_y = altura // 2
amplitud_max_pix = altura // 2 - 1

# Saltamos muestras para aligerar
salto_muestras = 100000  # ajusta a tu gusto

for i in range(0, numerosamples, salto_muestras):
    x_centro = int(i * paso_x)

    amp_norm = muestras[i] / max_val  # entre -1 y 1
    y_top = int(centro_y - amp_norm * amplitud_max_pix)
    y_bottom = int(centro_y + amp_norm * amplitud_max_pix)

    # Aseguramos que top < bottom
    if y_top > y_bottom:
        y_top, y_bottom = y_bottom, y_top

    # Dibujamos una cápsula vertical (rectángulo con esquinas redondeadas)
    draw.rounded_rectangle(
        (
            x_centro - radio,  # left
            y_top,             # top
            x_centro + radio,  # right
            y_bottom           # bottom
        ),
        radius=radio,
        fill=color_trazo,
        outline=color_trazo
    )

img.save("linea_capsula.png")
img.show()

