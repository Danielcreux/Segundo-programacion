from PIL import Image
import time
from concurrent.futures import ThreadPoolExecutor

def process_chunk_fast(args):
    """
    Procesa un fragmento de manera eficiente sin NumPy.
    """
    img_data, img_size, start_y, end_y, chunk_id = args
    
    # Recrear imagen desde bytes y cortar el fragmento
    img = Image.frombytes('RGB', img_size, img_data)
    chunk = img.crop((0, start_y, img_size[0], end_y))
    
    # Procesar TODOS los píxeles de una vez (más rápido que píxel por píxel)
    pixels = list(chunk.getdata())  # Obtener todos los píxeles como lista
    # Aplicar negativo a todos los píxeles
    processed_pixels = [(255 - r, 255 - g, 255 - b) for r, g, b in pixels]
    # Poner todos los píxeles procesados de vuelta
    chunk.putdata(processed_pixels)
    
    return chunk, start_y

def main():
    """
    Versión optimizada sin NumPy que es mucho más rápida que la original.
    """
    nucleos = 16
    inicio = time.time()
    
    try:
        # Cargar imagen una sola vez y convertir a bytes
        img = Image.open("Laia.jpg").convert('RGB')
        tamanio = img.size
        img_data = img.tobytes()  # Convertir a bytes para compartir entre hilos
        
        # Calcular fragmentos
        chunk_height = tamanio[1] // nucleos
        remaining_pixels = tamanio[1] % nucleos
        
        # Preparar argumentos para cada hilo
        chunks_args = []
        start_y = 0
        
        for i in range(nucleos):
            end_y = start_y + chunk_height
            if i < remaining_pixels:
                end_y += 1
            end_y = min(end_y, tamanio[1])
            
            chunks_args.append((img_data, tamanio, start_y, end_y, i))
            start_y = end_y
        
        # Procesar en paralelo
        with ThreadPoolExecutor(max_workers=nucleos) as executor:
            results = list(executor.map(process_chunk_fast, chunks_args))
        
        # Ordenar y combinar resultados
        results.sort(key=lambda x: x[1])  # Ordenar por start_y
        
        new_img = Image.new('RGB', tamanio)
        y_offset = 0
        
        for chunk, start_y in results:
            new_img.paste(chunk, (0, y_offset))
            y_offset += chunk.size[1]
        
        new_img.save("Laia3_rapida.jpg")
        print("✓ Imagen procesada correctamente")
        
    except FileNotFoundError:
        print("✗ Error: No se encontró el archivo 'Laia.jpg'")
        return
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    final = time.time()
    tiempo_total = final - inicio
    print(f"⏱️  Tiempo total: {tiempo_total:.3f} segundos con {nucleos} hilos")

def version_original():
    """
    Versión original para comparar velocidad.
    """
    inicio = time.time()
    
    img = Image.open("Laia.jpg")
    tamanio = img.size
    nucleos = 16
    bloquealtura = int(tamanio[1] / nucleos)

    box = (0, 0, tamanio[0], bloquealtura)
    recortado = img.crop(box)

    pixels = recortado.load()
    for x in range(0, tamanio[0]):
        for y in range(0, bloquealtura):
            pixel = recortado.getpixel((x,y))
            pixels[x, y] = (255 - pixel[0], 255 - pixel[1], 255 - pixel[2])
    
    recortado.save("Laia3_original.jpg")
    
    final = time.time()
    print(f"⏱️  Tiempo versión ORIGINAL: {final - inicio:.3f} segundos")

if __name__ == "__main__":
    print("=== PROCESAMIENTO DE IMAGEN CON HILOS ===")
    print("Ejecutando versión OPTIMIZADA...")
    main()
    
    print("\nEjecutando versión ORIGINAL para comparar...")
    version_original()