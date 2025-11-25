import librosa
import numpy as np

# Cargar el archivo MP3
archivo = "0802.mp3"
samples, sample_rate = librosa.load(archivo, sr=None, mono=True)

print("✅ Audio cargado correctamente!")
print(f"Total de muestras: {len(samples):,}")
print(f"Tasa de muestreo: {sample_rate} Hz")
print(f"Duración: {len(samples) / sample_rate:.2f} segundos")
print(f"Tipo de datos: {samples.dtype}")

# Mostrar las primeras muestras
print("\nPrimeras 20 muestras:")
for i, sample in enumerate(samples[:20]):
    print(f"Muestra {i}: {sample}")