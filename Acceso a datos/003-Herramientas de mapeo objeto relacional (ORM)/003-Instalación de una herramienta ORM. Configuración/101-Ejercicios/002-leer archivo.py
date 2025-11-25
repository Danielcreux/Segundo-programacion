from pydub import AudioSegment
import numpy as np

# Cargar MP3
audio = AudioSegment.from_mp3("0802.mp3")

# Convertir a array de muestras
samples = np.array(audio.get_array_of_samples())

print("Total samples:", len(samples))
for sample in samples:
  print(sample)

