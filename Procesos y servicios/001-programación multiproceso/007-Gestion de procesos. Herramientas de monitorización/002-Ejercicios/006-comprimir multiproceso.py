import multiprocessing
import os
import zipfile

# Configuración
carpeta = "C:\\Users\\Valentina\\Desktop\\muchovideos"

def comprimir(archivo):
    ruta_archivo = os.path.join(carpeta, archivo)
    # Solo archivos regulares y evitamos recomprimir .zip
    if not os.path.isfile(ruta_archivo) or archivo.endswith(".zip"):
        return
    ruta_zip = os.path.join(carpeta, archivo + ".zip")
    # Si ya existe el zip, lo saltamos (evitar trabajo innecesario)
    if os.path.exists(ruta_zip):
        return
    # Comprimir
    with zipfile.ZipFile(ruta_zip, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        # Guardamos sin la ruta absoluta dentro del zip
        z.write(ruta_archivo, arcname=archivo)
    print(f"Comprimido: {archivo} -> {archivo}.zip")

if __name__ == "__main__":
    num_cores = multiprocessing.cpu_count()
    print(f"Tienes {num_cores} núcleos de CPU.")

    # Listado de archivos a procesar
    archivos = os.listdir(carpeta)

    # Ejecutamos en paralelo: un proceso por núcleo
    with multiprocessing.Pool(processes=num_cores) as pool:
        pool.map(comprimir, archivos)

    print("Proceso de compresión finalizado.")
