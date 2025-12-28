## **Introducción**

Este script en Python es un **procesador avanzado de imágenes en paralelo**. Su objetivo es automatizar el post-procesamiento de un conjunto de imágenes grandes para generar versiones derivadas de cada una:

1. **Thumbnail** (miniatura) de la imagen.
2. **Versión en escala de grises**.
3. **Versión con borde artístico**.

Además, el programa:

* Mantiene la **rotación original** de las imágenes mediante la información Exif.
* Utiliza **multiprocesamiento** para acelerar el procesamiento aprovechando **todos los núcleos del CPU**.
* Muestra **progreso en tiempo real** de las imágenes procesadas.
* Guarda un **CSV con estadísticas** sobre cada imagen procesada.

---

## **Explicación paso a paso**

### Importación y configuración de carpetas

```python
import os
import csv
from PIL import Image, ExifTags, ImageOps
from multiprocessing import Pool, cpu_count, Manager, Lock
```

* Se importan las librerías necesarias: `PIL` para manipulación de imágenes, `os` para manejo de archivos, `multiprocessing` para paralelizar tareas y `csv` para guardar estadísticas.

```python
input_folder = "2024-28"       
output_folder = "procesadas"
os.makedirs(output_folder, exist_ok=True)
```

* Define la carpeta de entrada y salida.
* `os.makedirs(..., exist_ok=True)` crea las carpetas si no existen.

```python
thumb_folder = os.path.join(output_folder, "thumbnail")
gray_folder = os.path.join(output_folder, "grayscale")
border_folder = os.path.join(output_folder, "border")
for folder in [thumb_folder, gray_folder, border_folder]:
    os.makedirs(folder, exist_ok=True)
```

* Se crean subcarpetas para cada tipo de imagen derivada: thumbnail, escala de grises y borde.

```python
thumbnail_size = (150, 150)
border_size = 10
```

* Define el tamaño del thumbnail y el grosor del borde artístico.

---

### Función para corregir la rotación según Exif

```python
def corregir_orientacion(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            ori = exif.get(orientation, None)
            if ori == 3:
                img = img.rotate(180, expand=True)
            elif ori == 6:
                img = img.rotate(270, expand=True)
            elif ori == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img
```

* Las cámaras guardan la orientación de la foto en **Exif**.
* Esta función revisa la etiqueta `Orientation` y rota la imagen correctamente antes de procesarla.
* Evita que los thumbnails o imágenes derivadas queden rotadas incorrectamente.

---

### Función para procesar cada imagen

```python
def procesar_imagen(args):
    filename, counter, lock, total = args
    stats = {}
    stats['nombre'] = filename
```

* Se reciben los argumentos: nombre de archivo, contador de progreso, lock para sincronización y total de imágenes.
* Se inicializa un diccionario `stats` para guardar información de la imagen.

```python
    try:
        img_path = os.path.join(input_folder, filename)
        with Image.open(img_path) as img:
            img = corregir_orientacion(img)
```

* Se abre la imagen y se corrige la orientación.

#### a) Generación de Thumbnail

```python
            thumb = img.copy()
            thumb.thumbnail(thumbnail_size)
            thumb.save(os.path.join(thumb_folder, filename))
```

* Se hace una copia de la imagen original, se redimensiona y se guarda en la carpeta de thumbnails.

#### b) Escala de grises

```python
            gray = img.convert("L")
            gray.save(os.path.join(gray_folder, filename))
```

* Se convierte la imagen a modo “L” (blanco y negro) y se guarda.

#### c) Borde artístico

```python
            bordered = ImageOps.expand(img, border=border_size, fill='red')
            bordered.save(os.path.join(border_folder, filename))
```

* Se agrega un borde rojo de 10 px alrededor de la imagen y se guarda.

```python
            stats['ancho_original'], stats['alto_original'] = img.size
            stats['success'] = True
```

* Se registran dimensiones originales y estado de éxito.

#### Manejo de errores

```python
    except Exception as e:
        stats['success'] = False
        stats['error'] = str(e)
```

* Si ocurre un error al procesar la imagen, se registra en `stats` para reportarlo luego.

#### Actualización de progreso

```python
    with lock:
        counter.value += 1
        print(f"Procesadas {counter.value}/{total} imágenes", end="\r")
```

* Se usa un **lock** para sincronizar prints entre procesos.
* Se incrementa el contador y se muestra el progreso en tiempo real.

---

### Parte principal (Main)

```python
if __name__ == "__main__":
    imagenes = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_images = len(imagenes)
```

* Se listan todas las imágenes de la carpeta de entrada.

```python
    manager = Manager()
    counter = manager.Value('i', 0)
    lock = manager.Lock()
```

* Se crean objetos compartidos para **contador** y **lock**, que serán usados por los procesos.

```python
    args_list = [(img, counter, lock, total_images) for img in imagenes]
    with Pool(cpu_count()) as pool:
        resultados = pool.map(procesar_imagen, args_list)
```

* Se crea un **Pool de procesos** igual al número de núcleos del CPU.
* Cada proceso recibe su archivo y argumentos para procesarlo en paralelo.

#### Guardar estadísticas en CSV

```python
    csv_file = os.path.join(output_folder, "estadisticas.csv")
    keys = resultados[0].keys() if resultados else []
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(resultados)
```

* Se crea un CSV con el nombre, dimensiones y estado de éxito de cada imagen.

```python
    print(f"\n Procesamiento completado. Estadísticas guardadas en {csv_file}")
```
## **Conclusión**

Este script es una base excelente para proyectos de **gestión de imágenes, galerías web, generación de previews y efectos artísticos automatizados**.

