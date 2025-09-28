#!/usr/bin/env python3
"""
StegoTexto Web App - Aplicación Flask para codificación/decodificación web
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import json
from datetime import datetime
from PIL import Image
import math
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stegotexto_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Crear directorio para imágenes generadas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def codificar_texto(texto_entrada, archivo_salida):
    """
    Codifica un texto en una imagen RGB.
    
    Args:
        texto_entrada (str): Texto a codificar
        archivo_salida (str): Ruta del archivo de imagen de salida
    
    Returns:
        dict: Información sobre la codificación
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
        img.save(archivo_salida, optimize=True)
        
        # Obtener información del archivo
        file_size = os.path.getsize(archivo_salida)
        file_size_kb = round(file_size / 1024, 2)
        
        return {
            'success': True,
            'image_size': f"{lado_imagen}x{lado_imagen} pixels ({file_size_kb} KB)",
            'data_length': longitud_original,
            'dimensions': f"{lado_imagen}x{lado_imagen}"
        }
        
    except Exception as e:
        print(f"❌ Error durante la codificación: {e}")
        return {
            'success': False,
            'error': str(e)
        }


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


@app.route('/')
def index():
    """Página principal de la aplicación."""
    return render_template('index.html')


@app.route('/encode', methods=['POST'])
def encode_data():
    """Endpoint para codificar datos del usuario en una imagen."""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['name', 'surname', 'email', 'phone', 'filename']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Crear texto a codificar (formato estructurado)
        user_data = {
            'nombre': data['name'].strip(),
            'apellido': data['surname'].strip(),
            'email': data['email'].strip(),
            'telefono': data['phone'].strip(),
            'fecha_codificacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Convertir a texto para codificación
        texto_a_codificar = json.dumps(user_data, ensure_ascii=False, indent=2)
        
        # Generar nombre de archivo
        filename_base = data['filename'].strip()
        if not filename_base.endswith('.png'):
            filename_base += '.png'
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_base)
        
        # Codificar el texto en la imagen
        result = codificar_texto(texto_a_codificar, output_path)
        
        if result['success']:
            # Devolver información al cliente
            return jsonify({
                'success': True,
                'image_url': f'/static/generated/{filename_base}',
                'filename': filename_base,
                'image_size': result['image_size'],
                'data_length': result['data_length'],
                'dimensions': result['dimensions']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        print(f"❌ Error en endpoint /encode: {e}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500


@app.route('/decode', methods=['POST'])
def decode_data():
    """Endpoint para decodificar datos desde una imagen."""
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se proporcionó ninguna imagen'
            }), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó ningún archivo'
            }), 400
        
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            image_file.save(temp_file.name)
            temp_path = temp_file.name
        
        # Decodificar la imagen
        decoded_text = decodificar_imagen(temp_path)
        
        # Limpiar archivo temporal
        os.unlink(temp_path)
        
        if decoded_text:
            try:
                # Intentar parsear como JSON
                user_data = json.loads(decoded_text)
                return jsonify({
                    'success': True,
                    'data': user_data,
                    'raw_text': decoded_text
                })
            except json.JSONDecodeError:
                # Si no es JSON válido, devolver texto plano
                return jsonify({
                    'success': True,
                    'data': None,
                    'raw_text': decoded_text
                })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo decodificar la imagen o no contiene datos válidos'
            }), 400
            
    except Exception as e:
        print(f"❌ Error en endpoint /decode: {e}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Endpoint para descargar imágenes generadas."""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado'
            }), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        print(f"❌ Error descargando archivo: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al descargar el archivo'
        }), 500


# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    print("🚀 Iniciando StegoTexto Web App...")
    print("📁 Directorio de trabajo:", os.getcwd())
    print("📁 Imágenes generadas:", app.config['UPLOAD_FOLDER'])
    
    # Verificar que el directorio de templates existe
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Directorio 'templates' creado")
    
    # Verificar que el directorio static existe
    if not os.path.exists('static'):
        os.makedirs('static')
        print("📁 Directorio 'static' creado")
    
    app.run(debug=True, host='0.0.0.0', port=5000)