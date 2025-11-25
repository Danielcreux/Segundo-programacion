from PIL import Image, ImageDraw
from pydub import AudioSegment
import numpy as np

audio = AudioSegment.from_mp3("0802.mp3")
samples = np.array(audio.get_array_of_samples())

anchura = 800
altura = 200

img = Image.new("RGB", (anchura, altura), "white")
draw = ImageDraw.Draw(img)

numerosamples = len(samples)

paso = anchura / numerosamples

max_val = np.max(np.abs(samples))
if max_val == 0:
    max_val = 1  

centro_y = altura // 2

for i in range(0, numerosamples, 100000):  # cada 100 muestras para aligerar
    x = int(i * paso)
    amp_norm = samples[i] / max_val
    y = int(centro_y + amp_norm * (altura // 2 - 1))
    draw.line((x, centro_y, x, y), fill="black", width=1)

img.save("linea.png")
img.show()

