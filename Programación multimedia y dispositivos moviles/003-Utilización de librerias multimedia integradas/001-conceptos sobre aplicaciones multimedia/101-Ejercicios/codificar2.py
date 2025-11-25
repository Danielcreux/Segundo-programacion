import json
import subprocess
import os
import argparse
from pathlib import Path

def get_video_resolution(input_video):
    """Obtiene la resolución del video usando ffprobe"""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            input_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split(','))
        return width, height
    except:
        return None, None

def get_resolutions_to_encode(original_width, original_height):
    """Genera lista de resoluciones desde la original hacia abajo"""
    resolutions = []
    
    # Resolución original
    resolutions.append((original_width, original_height, "original"))
    
    # Resoluciones estándar menores o iguales a la original
    standard_resolutions = [
        (3840, 2160, "4k"),
        (2560, 1440, "1440p"),
        (1920, 1080, "1080p"),
        (1280, 720, "720p"),
        (854, 480, "480p"),
        (640, 360, "360p"),
        (426, 240, "240p")
    ]
    
    # Agregar solo resoluciones menores o iguales a la original
    for width, height, name in standard_resolutions:
        if width <= original_width and height <= original_height:
            if not any(abs(w - width) < 50 and abs(h - height) < 50 for w, h, _ in resolutions):
                resolutions.append((width, height, name))
    
    return resolutions

def encode_video(input_video, output_dir, width, height, quality_name):
    """Codifica el video a una resolución específica con nombre estándar"""
    # Nombre de archivo estándar independiente del video original
    output_filename = f"video_{quality_name}.mp4"
    output_path = Path(output_dir) / output_filename
    
    cmd = [
        'ffmpeg',
        '-i', input_video,
        '-vf', f'scale={width}:{height}:flags=lanczos',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        '-loglevel', 'quiet',  # Silencia la salida de ffmpeg
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description='Codificar video a múltiples resoluciones')
    parser.add_argument('input_video', help='Ruta al video de entrada')
    parser.add_argument('-o', '--output-dir', default='output', help='Directorio de salida')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_video):
        print(f"Error: El archivo {args.input_video} no existe")
        return
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    original_width, original_height = get_video_resolution(args.input_video)
    
    if original_width is None or original_height is None:
        print("No se pudo obtener la resolución del video")
        return
    
    resolutions = get_resolutions_to_encode(original_width, original_height)
    
    video_files = {}
    completed = []
    
    for width, height, quality_name in resolutions:
        output_path = encode_video(args.input_video, args.output_dir, width, height, quality_name)
        if output_path:
            # Solo guardar el nombre del archivo, no la ruta completa
            video_files[quality_name] = {
                'filename': f"video_{quality_name}.mp4",  # Nombre estandarizado
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height
            }
            completed.append(quality_name)
            print(f"✓ {quality_name} ({width}x{height})")
    
    json_path = os.path.join(args.output_dir, 'video_versions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(video_files, f, indent=2, ensure_ascii=False)
    
    print(f"\nConversiones completadas: {len(completed)}")
    print(f"JSON: {json_path}")

if __name__ == "__main__":
    main()