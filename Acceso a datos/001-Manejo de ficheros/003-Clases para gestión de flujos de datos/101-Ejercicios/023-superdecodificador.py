#!/usr/bin/env python3
"""
StegoTexto - Codificador/Decodificador de Texto en Imágenes RGB

Este programa permite ocultar texto en imágenes RGB y recuperarlo posteriormente.
Cada píxel de la imagen almacena 3 caracteres (uno en cada canal R, G, B).

Autor: Asistente AI
Versión: 1.0
"""

from PIL import Image
import math
import argparse
import sys
import os


def codificar_texto(texto_entrada, archivo_salida):
    """
    Codifica un texto en una imagen RGB.
    
    Args:
        texto_entrada (str): Texto a codificar
        archivo_salida (str): Ruta del archivo de imagen de salida
    
    Returns:
        bool: True si la codificación fue exitosa, False en caso contrario
    """
    try:
        print("🔒 Iniciando codificación de texto...")
        
        # Convertir texto a lista de caracteres
        letras = list(texto_entrada)
        longitud_original = len(letras)
        
        # Calcular dimensiones de la imagen
        pixels_necesarios = math.ceil(len(letras) / 3)
        lado_imagen = math.ceil(math.sqrt(pixels_necesarios))
        
        # Asegurar que tenemos suficientes píxeles
        if lado_imagen * lado_imagen < pixels_necesarios:
            lado_imagen += 1
        
        print(f"📊 Longitud del texto: {longitud_original} caracteres")
        print(f"📐 Píxeles necesarios: {pixels_necesarios}")
        print(f"🖼️  Dimensiones de la imagen: {lado_imagen} x {lado_imagen}")
        
        # Rellenar con caracteres nulos para que sea divisible por 3
        while len(letras) % 3 != 0:
            letras.append('\0')
        
        # Crear imagen nueva
        img = Image.new("RGB", size=(lado_imagen, lado_imagen), color="white")
        pixels = img.load()
        
        # Codificar texto en los píxeles
        contador = 0
        for i in range(0, len(letras), 3):
            x = contador % lado_imagen
            y = contador // lado_imagen
            pixels[x, y] = (ord(letras[i]), ord(letras[i+1]), ord(letras[i+2]))
            contador += 1
        
        # Guardar imagen
        img.save(archivo_salida)
        print(f"✅ Texto codificado exitosamente en: {archivo_salida}")
        print(f"💾 Tamaño de la imagen: {lado_imagen}x{lado_imagen} píxeles")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la codificación: {e}")
        return False


def decodificar_imagen(archivo_entrada):
    """
    Decodifica texto desde una imagen RGB.
    
    Args:
        archivo_entrada (str): Ruta del archivo de imagen codificada
    
    Returns:
        str: Texto decodificado o None si hay error
    """
    try:
        print("🔓 Iniciando decodificación de imagen...")
        
        # Verificar que el archivo existe
        if not os.path.exists(archivo_entrada):
            print("❌ El archivo de entrada no existe")
            return None
        
        # Abrir imagen
        img = Image.open(archivo_entrada)
        pixels = img.load()
        tamaño = img.size
        
        print(f"🖼️  Imagen cargada: {tamaño[0]} x {tamaño[1]} píxeles")
        
        # Decodificar texto
        texto_decodificado = ""
        caracteres_decodificados = 0
        
        for y in range(tamaño[1]):
            for x in range(tamaño[0]):
                r, g, b = pixels[x, y]
                
                # Decodificar cada canal (detener en carácter nulo)
                if r != 0 and 32 <= r <= 126:  # Caracteres imprimibles ASCII
                    texto_decodificado += chr(r)
                    caracteres_decodificados += 1
                else:
                    r = 0
                
                if g != 0 and 32 <= g <= 126:
                    texto_decodificado += chr(g)
                    caracteres_decodificados += 1
                else:
                    g = 0
                
                if b != 0 and 32 <= b <= 126:
                    texto_decodificado += chr(b)
                    caracteres_decodificados += 1
                else:
                    b = 0
                
                # Si encontramos 3 caracteres nulos consecutivos, probablemente es el final
                if r == 0 and g == 0 and b == 0:
                    break
            else:
                continue
            break
        
        print(f"✅ Texto decodificado: {caracteres_decodificados} caracteres")
        return texto_decodificado
        
    except Exception as e:
        print(f"❌ Error durante la decodificación: {e}")
        return None


def mostrar_info():
    """Muestra información sobre el programa."""
    print("""
🤖 StegoTexto - Codificador/Decodificador de Texto en Imágenes RGB

CARACTERÍSTICAS:
• Codifica texto en imágenes PNG usando canales RGB
• Cada píxel almacena 3 caracteres (R, G, B)
• Soporta texto ASCII estándar
• Genera imágenes cuadradas optimizadas

MODO DE USO:
Codificar: python stegotexto.py -m codificar -i "texto" -o imagen.png
Decodificar: python stegotexto.py -m decodificar -i imagen.png

EJEMPLOS:
python stegotexto.py -m codificar -i "Hola mundo" -o secreto.png
python stegotexto.py -m decodificar -i secreto.png
    """)


def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(
        description="StegoTexto - Codifica/decodifica texto en imágenes RGB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  Codificar texto:  python %(prog)s -m codificar -i "Texto secreto" -o imagen.png
  Decodificar texto: python %(prog)s -m decodificar -i imagen.png
        """
    )
    
    parser.add_argument(
        "-m", "--modo",
        required=True,
        choices=["codificar", "decodificar"],
        help="Modo de operación: 'codificar' o 'decodificar'"
    )
    
    parser.add_argument(
        "-i", "--entrada",
        required=True,
        help="Texto de entrada (para codificar) o archivo de imagen (para decodificar)"
    )
    
    parser.add_argument(
        "-o", "--salida",
        help="Archivo de imagen de salida (solo para modo codificar)"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar información del programa"
    )
    
    # Procesar argumentos
    args = parser.parse_args()
    
    # Mostrar información si se solicita
    if args.info:
        mostrar_info()
        return
    
    # Ejecutar según el modo seleccionado
    if args.modo == "codificar":
        if not args.salida:
            print("❌ Error: Se requiere el argumento -o/--salida para el modo codificar")
            sys.exit(1)
        
        # Verificar extensión del archivo de salida
        if not args.salida.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            print("⚠️  Advertencia: Se recomienda usar formato PNG para mejor calidad")
        
        éxito = codificar_texto(args.entrada, args.salida)
        if not éxito:
            sys.exit(1)
            
    elif args.modo == "decodificar":
        texto = decodificar_imagen(args.entrada)
        if texto is not None:
            print("\n" + "="*50)
            print("📄 TEXTO DECODIFICADO:")
            print("="*50)
            print(texto)
            print("="*50)
        else:
            sys.exit(1)


if __name__ == "__main__":
    # Banner de presentación
    print("🔐 StegoTexto - Codificador/Decodificador v1.0")
    print("=" * 50)
    
    # Ejecutar programa principal
    main()