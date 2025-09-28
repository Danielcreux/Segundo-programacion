from PIL import Image, ImageFilter
import time
from concurrent.futures import ThreadPoolExecutor

def process_chunk_gaussian(args):
    """
    Aplica desenfoque gaussiano a un fragmento de la imagen.
    """
    img_data, img_size, start_y, end_y, chunk_id = args
    
    # Recrear imagen desde bytes y cortar el fragmento
    img = Image.frombytes('RGB', img_size, img_data)
    chunk = img.crop((0, start_y, img_size[0], end_y))
    
    # Aplicar filtro gaussiano (operación más intensiva que el negativo)
    blurred_chunk = chunk.filter(ImageFilter.GaussianBlur(radius=3))
    
    return blurred_chunk, start_y

def process_chunk_negative(args):
    """
    Aplica negativo a un fragmento (para comparación).
    """
    img_data, img_size, start_y, end_y, chunk_id = args
    
    # Recrear imagen desde bytes y cortar el fragmento
    img = Image.frombytes('RGB', img_size, img_data)
    chunk = img.crop((0, start_y, img_size[0], end_y))
    
    # Procesar TODOS los píxeles de una vez
    pixels = list(chunk.getdata())
    processed_pixels = [(255 - r, 255 - g, 255 - b) for r, g, b in pixels]
    chunk.putdata(processed_pixels)
    
    return chunk, start_y

def main_gaussian():
    """
    Versión con desenfoque gaussiano usando hilos.
    """
    nucleos = 16
    inicio = time.time()
    
    try:
        # Cargar imagen una sola vez y convertir a bytes
        img = Image.open("Laia.jpg").convert('RGB')
        tamanio = img.size
        img_data = img.tobytes()
        
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
            results = list(executor.map(process_chunk_gaussian, chunks_args))
        
        # Ordenar y combinar resultados
        results.sort(key=lambda x: x[1])
        
        new_img = Image.new('RGB', tamanio)
        y_offset = 0
        
        for chunk, start_y in results:
            new_img.paste(chunk, (0, y_offset))
            y_offset += chunk.size[1]
        
        new_img.save("Laia3_gaussian_threads.jpg")
        print("✓ Imagen con desenfoque gaussiano procesada correctamente")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    final = time.time()
    tiempo_total = final - inicio
    print(f"⏱️  Tiempo GAUSSIANO con hilos: {tiempo_total:.3f} segundos")
    return tiempo_total

def main_negative():
    """
    Versión con negativo usando hilos.
    """
    nucleos = 16
    inicio = time.time()
    
    try:
        img = Image.open("Laia.jpg").convert('RGB')
        tamanio = img.size
        img_data = img.tobytes()
        
        chunk_height = tamanio[1] // nucleos
        remaining_pixels = tamanio[1] % nucleos
        
        chunks_args = []
        start_y = 0
        
        for i in range(nucleos):
            end_y = start_y + chunk_height
            if i < remaining_pixels:
                end_y += 1
            end_y = min(end_y, tamanio[1])
            
            chunks_args.append((img_data, tamanio, start_y, end_y, i))
            start_y = end_y
        
        with ThreadPoolExecutor(max_workers=nucleos) as executor:
            results = list(executor.map(process_chunk_negative, chunks_args))
        
        results.sort(key=lambda x: x[1])
        new_img = Image.new('RGB', tamanio)
        y_offset = 0
        
        for chunk, start_y in results:
            new_img.paste(chunk, (0, y_offset))
            y_offset += chunk.size[1]
        
        new_img.save("Laia3_negative_threads.jpg")
        print("✓ Imagen con negativo procesada correctamente")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    final = time.time()
    tiempo_total = final - inicio
    print(f"⏱️  Tiempo NEGATIVO con hilos: {tiempo_total:.3f} segundos")
    return tiempo_total

def gaussian_original():
    """
    Versión original con desenfoque gaussiano (sin hilos).
    """
    inicio = time.time()
    
    try:
        img = Image.open("Laia.jpg").convert('RGB')
        tamanio = img.size
        
        # Aplicar desenfoque gaussiano a toda la imagen
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=3))
        blurred_img.save("Laia3_gaussian_original.jpg")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    final = time.time()
    tiempo_total = final - inicio
    print(f"⏱️  Tiempo GAUSSIANO original: {tiempo_total:.3f} segundos")
    return tiempo_total

def negative_original():
    """
    Versión original con negativo (sin hilos).
    """
    inicio = time.time()
    
    try:
        img = Image.open("Laia.jpg").convert('RGB')
        tamanio = img.size
        
        # Aplicar negativo a toda la imagen
        pixels = list(img.getdata())
        processed_pixels = [(255 - r, 255 - g, 255 - b) for r, g, b in pixels]
        img.putdata(processed_pixels)
        img.save("Laia3_negative_original.jpg")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    final = time.time()
    tiempo_total = final - inicio
    print(f"⏱️  Tiempo NEGATIVO original: {tiempo_total:.3f} segundos")
    return tiempo_total

def calculate_improvement(original_time, threaded_time):
    """Calcula la mejora de velocidad."""
    if original_time and threaded_time:
        improvement = ((original_time - threaded_time) / original_time) * 100
        return improvement
    return 0

if __name__ == "__main__":
    print("=== COMPARACIÓN DE OPERACIONES CON HILOS ===")
    print("Operaciones: Desenfoque Gaussiano vs Negativo")
    print("=" * 50)
    
    # Procesar ambas operaciones con hilos
    print("\n1. EJECUTANDO VERSIONES CON HILOS:")
    print("-" * 30)
    gaussian_threaded = main_gaussian()
    
    print()
    negative_threaded = main_negative()
    
    # Procesar ambas operaciones sin hilos
    print("\n2. EJECUTANDO VERSIONES ORIGINALES (sin hilos):")
    print("-" * 40)
    gaussian_original_time = gaussian_original()
    
    print()
    negative_original_time = negative_original()
    
    # Mostrar comparación
    print("\n3. RESULTADOS DE MEJORA:")
    print("-" * 25)
    
    if gaussian_original_time and gaussian_threaded:
        gaussian_improvement = calculate_improvement(gaussian_original_time, gaussian_threaded)
        print(f"🔵 GAUSSIANO: {gaussian_improvement:+.1f}% de mejora")
        print(f"   Original: {gaussian_original_time:.3f}s → Con hilos: {gaussian_threaded:.3f}s")
    
    if negative_original_time and negative_threaded:
        negative_improvement = calculate_improvement(negative_original_time, negative_threaded)
        print(f"🔴 NEGATIVO: {negative_improvement:+.1f}% de mejora")
        print(f"   Original: {negative_original_time:.3f}s → Con hilos: {negative_threaded:.3f}s")
    
    print("\n4. EXPLICACIÓN:")
    print("-" * 15)
    print("• El desenfoque gaussiano es una operación MÁS INTENSIVA")
    print("• Se beneficia MÁS del paralelismo porque cada fragmento")
    print("  requiere más tiempo de procesamiento individual")
    print("• El negativo es una operación simple donde el overhead")
    print("  de los hilos puede ser más significativo")