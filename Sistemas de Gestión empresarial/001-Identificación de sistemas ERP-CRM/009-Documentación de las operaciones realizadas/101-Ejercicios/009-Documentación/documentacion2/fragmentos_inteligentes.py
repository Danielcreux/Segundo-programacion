# fragmentos_inteligentes.py
import ast
import re
from typing import List, Dict, Tuple, Optional

def extraer_fragmentos_clave(codigo: str, lenguaje: str, max_fragmentos: int = 5) -> List[Dict]:
    """
    Extrae los fragmentos más importantes del código para mostrar
    en lugar de todo el archivo completo.
    """
    fragmentos = []
    
    try:
        if lenguaje == "python":
            fragmentos = _analizar_python(codigo, max_fragmentos)
        elif lenguaje in ["javascript", "typescript", "js", "ts"]:
            fragmentos = _analizar_javascript(codigo, max_fragmentos)
        elif lenguaje == "html":
            fragmentos = _analizar_html(codigo, max_fragmentos)
        elif lenguaje == "css":
            fragmentos = _analizar_css(codigo, max_fragmentos)
        else:
            fragmentos = _analizar_generico(codigo, max_fragmentos)
    except Exception as e:
        # Fallback a análisis genérico
        fragmentos = _analizar_generico(codigo, max_fragmentos)
    
    return fragmentos[:max_fragmentos]

def _analizar_python(codigo: str, max_fragmentos: int) -> List[Dict]:
    """Analiza código Python y extrae funciones, clases y estructuras clave"""
    fragmentos = []
    
    try:
        arbol = ast.parse(codigo)
        
        for nodo in ast.walk(arbol):
            if len(fragmentos) >= max_fragmentos:
                break
                
            if isinstance(nodo, ast.FunctionDef):
                # Función
                start_line = nodo.lineno
                end_line = nodo.end_lineno or start_line
                codigo_funcion = _extraer_lineas(codigo, start_line, end_line)
                
                fragmentos.append({
                    "tipo": "función",
                    "nombre": nodo.name,
                    "codigo": codigo_funcion,
                    "linea_inicio": start_line,
                    "linea_fin": end_line,
                    "descripcion": f"Función {nodo.name}()"
                })
                
            elif isinstance(nodo, ast.ClassDef):
                # Clase
                start_line = nodo.lineno
                end_line = nodo.end_lineno or start_line
                codigo_clase = _extraer_lineas(codigo, start_line, min(end_line, start_line + 10))
                
                fragmentos.append({
                    "tipo": "clase", 
                    "nombre": nodo.name,
                    "codigo": codigo_clase,
                    "linea_inicio": start_line,
                    "linea_fin": end_line,
                    "descripcion": f"Clase {nodo.name}"
                })
                
    except SyntaxError:
        # Si hay error de sintaxis, usar análisis genérico
        return _analizar_generico(codigo, max_fragmentos)
    
    # Si no encontramos suficientes fragmentos, agregar importaciones
    if len(fragmentos) < max_fragmentos:
        imports = _extraer_imports_python(codigo)
        for imp in imports[:max_fragmentos - len(fragmentos)]:
            fragmentos.append(imp)
    
    return fragmentos

def _analizar_javascript(codigo: str, max_fragmentos: int) -> List[Dict]:
    """Analiza código JavaScript/TypeScript"""
    fragmentos = []
    
    # Patrones regex para funciones y clases
    patrones = [
        (r'(export\s+)?(async\s+)?function\s+(\w+)', 'función'),
        (r'(export\s+)?class\s+(\w+)', 'clase'),
        (r'const\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>', 'función flecha'),
        (r'let\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>', 'función flecha'),
        (r'var\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>', 'función flecha'),
    ]
    
    lineas = codigo.split('\n')
    
    for i, linea in enumerate(lineas):
        if len(fragmentos) >= max_fragmentos:
            break
            
        for patron, tipo in patrones:
            match = re.search(patron, linea.strip())
            if match:
                nombre = match.group(3) if 'function' in patron else match.group(2) if 'class' in patron else match.group(1)
                
                # Extraer bloque de código (siguientes 10-15 líneas)
                start_line = i + 1
                end_line = min(i + 15, len(lineas))
                codigo_bloque = '\n'.join(lineas[i:end_line])
                
                fragmentos.append({
                    "tipo": tipo,
                    "nombre": nombre,
                    "codigo": codigo_bloque,
                    "linea_inicio": start_line,
                    "linea_fin": end_line,
                    "descripcion": f"{tipo.title()} {nombre}"
                })
                break
    
    return fragmentos

def _analizar_html(codigo: str, max_fragmentos: int) -> List[Dict]:
    """Analiza HTML y extrae secciones importantes"""
    fragmentos = []
    
    # Patrones para elementos HTML importantes
    patrones = [
        (r'<script[^>]*>', '</script>', 'script'),
        (r'<style[^>]*>', '</style>', 'styles'),
        (r'<form[^>]*>', '</form>', 'formulario'),
        (r'<main[^>]*>', '</main>', 'contenido principal'),
        (r'<header[^>]*>', '</header>', 'cabecera'),
        (r'<nav[^>]*>', '</nav>', 'navegación'),
    ]
    
    for patron_inicio, patron_fin, tipo in patrones:
        if len(fragmentos) >= max_fragmentos:
            break
            
        inicio = re.search(patron_inicio, codigo)
        if inicio:
            # Buscar el cierre correspondiente
            resto = codigo[inicio.start():]
            fin = re.search(patron_fin, resto)
            
            if fin:
                codigo_bloque = resto[:fin.end()]
                fragmentos.append({
                    "tipo": tipo,
                    "nombre": f"bloque_{tipo}",
                    "codigo": codigo_bloque,
                    "linea_inicio": codigo[:inicio.start()].count('\n') + 1,
                    "descripcion": f"Sección {tipo}"
                })
    
    return fragmentos

def _analizar_css(codigo: str, max_fragmentos: int) -> List[Dict]:
    """Analiza CSS y extrae reglas importantes"""
    fragmentos = []
    
    # Encontrar bloques CSS (selectores + { ... })
    patron = r'([^{]+)\{([^}]+)\}'
    matches = re.finditer(patron, codigo, re.DOTALL)
    
    for match in list(matches)[:max_fragmentos]:
        selector = match.group(1).strip()
        propiedades = match.group(2).strip()
        
        if selector and propiedades:
            fragmentos.append({
                "tipo": "regla_css",
                "nombre": selector,
                "codigo": f"{selector} {{\n{propiedades}\n}}",
                "descripcion": f"Regla CSS: {selector}"
            })
    
    return fragmentos

def _analizar_generico(codigo: str, max_fragmentos: int) -> List[Dict]:
    """Análisis genérico para cualquier lenguaje"""
    fragmentos = []
    lineas = codigo.split('\n')
    
    # Buscar líneas que parecen importantes (contienen palabras clave)
    palabras_clave = ['def ', 'class ', 'function ', 'export ', 'import ', 'const ', 'let ', 'var ', '<div', '<script', '<style']
    
    for i, linea in enumerate(lineas):
        if len(fragmentos) >= max_fragmentos:
            break
            
        if any(palabra in linea for palabra in palabras_clave):
            # Tomar esta línea y las siguientes 5-10
            start_line = i + 1
            end_line = min(i + 10, len(lineas))
            codigo_bloque = '\n'.join(lineas[i:end_line])
            
            fragmentos.append({
                "tipo": "fragmento",
                "nombre": f"linea_{start_line}",
                "codigo": codigo_bloque,
                "linea_inicio": start_line,
                "linea_fin": end_line,
                "descripcion": f"Fragmento línea {start_line}"
            })
    
    return fragmentos

def _extraer_lineas(codigo: str, inicio: int, fin: int) -> str:
    """Extrae un rango de líneas del código"""
    lineas = codigo.split('\n')
    return '\n'.join(lineas[inicio-1:fin])

def _extraer_imports_python(codigo: str) -> List[Dict]:
    """Extrae importaciones de Python"""
    imports = []
    lineas = codigo.split('\n')
    
    for i, linea in enumerate(lineas):
        if linea.strip().startswith(('import ', 'from ')):
            imports.append({
                "tipo": "importación",
                "nombre": linea.strip(),
                "codigo": linea,
                "linea_inicio": i + 1,
                "descripcion": "Importación"
            })
    
    return imports