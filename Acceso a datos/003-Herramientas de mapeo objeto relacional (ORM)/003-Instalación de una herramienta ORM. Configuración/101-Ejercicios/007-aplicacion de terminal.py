#!/usr/bin/env python3
"""
wavecaps.py

Pequeña utilidad de consola para generar una “waveform” en forma de cápsulas
redondeadas a partir de un archivo MP3.

Uso básico (ejemplo):

    python wavecaps.py \
        --input 0802.mp3 \
        --output linea_capsula.png \
        --width 800 \
        --height 200 \
        --samples 300 \
        --thickness 6

Parámetros
----------
--input / -i
    Ruta del archivo MP3 de entrada.

--output / -o
    Ruta del archivo de imagen de salida (PNG, JPG, etc. según la extensión).

--width / -W
    Anchura de la imagen en píxeles.

--height / -H
    Altura de la imagen en píxeles.

--samples / -n
    Número de “barras” visuales (cápsulas) que se dibujarán a lo largo de la
    anchura de la imagen. A partir de este valor se calcula el salto de muestras
    del audio para representar toda la forma de onda de manera comprimida.

--thickness / -t
    Grosor de cada cápsula (en píxeles). Internamente se usa para calcular el
    radio de las puntas redondeadas.

Notas
-----
- El audio se convierte a mono si tiene más de un canal (promedio L/R) para que
  la onda no quede intercalada.
- La amplitud se normaliza para usar todo el rango vertical disponible.
- Si el archivo de audio es muy largo, un número de muestras visuales muy alto
  puede ralentizar el proceso o producir una imagen muy “densa”.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw
from pydub import AudioSegment
import numpy as np


def generar_waveform_capsulas(
    input_mp3: str,
    output_img: str,
    anchura: int,
    altura: int,
    num_visual_samples: int,
    grosor: int,
    color_fondo: str = "white",
    color_trazo: str = "black",
) -> None:
    """
    Genera una imagen de waveform en forma de cápsulas redondeadas.

    Parameters
    ----------
    input_mp3 : str
        Ruta al archivo MP3 de entrada.
    output_img : str
        Ruta al archivo de imagen que se generará.
    anchura : int
        Anchura de la imagen en píxeles.
    altura : int
        Altura de la imagen en píxeles.
    num_visual_samples : int
        Número de muestras “visuales” (barras/cápsulas) a dibujar.
    grosor : int
        Grosor de cada cápsula en píxeles.
    color_fondo : str, opcional
        Color de fondo de la imagen (por defecto "white").
    color_trazo : str, opconal
        Color del trazo/cápsulas (por defecto "black").
    """

    # --- Carga del audio ---
    audio = AudioSegment.from_mp3(input_mp3)

    # Aseguramos mono para que no se mezclen canales L/R intercalados
    if audio.channels > 1:
        muestras = np.array(audio.get_array_of_samples()).reshape((-1, audio.channels))
        muestras = muestras.mean(axis=1)
    else:
        muestras = np.array(audio.get_array_of_samples())

    numerosamples = len(muestras)
    if numerosamples == 0:
        raise ValueError("El archivo de audio no contiene muestras.")

    # --- Cálculo del salto de muestras a partir del número de muestras visuales ---
    # Queremos cubrir todo el audio con 'num_visual_samples' posiciones en X.
    # Aseguramos que el salto sea al menos 1 para evitar divisiones por cero.
    salto_muestras = max(1, numerosamples // max(1, num_visual_samples))

    # --- Creación de la imagen ---
    img = Image.new("RGB", (anchura, altura), color_fondo)
    draw = ImageDraw.Draw(img)

    # Relación índice de muestra → X en la imagen
    paso_x = anchura / numerosamples

    # Normalización de la amplitud
    max_val = np.max(np.abs(muestras))
    if max_val == 0:
        max_val = 1  # evitamos división por cero si el audio es completamente silencioso

    centro_y = altura // 2
    amplitud_max_pix = altura // 2 - 1

    radio = max(1, grosor // 2)  # radio para las puntas redondeadas

    # --- Dibujamos las cápsulas ---
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

    # Guardamos la imagen en disco
    img.save(output_img)


def parse_args() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Genera una imagen de waveform con cápsulas redondeadas a partir de un MP3."
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Archivo MP3 de entrada."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Archivo de imagen de salida (por ejemplo, output.png)."
    )
    parser.add_argument(
        "-W", "--width",
        type=int,
        default=800,
        help="Anchura de la imagen en píxeles (por defecto: 800)."
    )
    parser.add_argument(
        "-H", "--height",
        type=int,
        default=200,
        help="Altura de la imagen en píxeles (por defecto: 200)."
    )
    parser.add_argument(
        "-n", "--samples",
        type=int,
        default=300,
        help="Número de muestras visuales/barras (por defecto: 300)."
    )
    parser.add_argument(
        "-t", "--thickness",
        type=int,
        default=6,
        help="Grosor de cada cápsula en píxeles (por defecto: 6)."
    )

    return parser.parse_args()


def main() -> None:
    """Punto de entrada principal del script."""
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {input_path}")

    generar_waveform_capsulas(
        input_mp3=str(input_path),
        output_img=args.output,
        anchura=args.width,
        altura=args.height,
        num_visual_samples=args.samples,
        grosor=args.thickness,
    )


if __name__ == "__main__":
    main()

