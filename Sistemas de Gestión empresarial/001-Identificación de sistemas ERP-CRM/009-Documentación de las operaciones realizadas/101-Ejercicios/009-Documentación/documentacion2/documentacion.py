# documentacion.py - VERSIÓN MEJORADA CON FRAGMENTOS
from arbol import draw_tree
from cabeceras_stream import write_markdown_stream
import os
import time

def generar_documentacion_completa():
    ruta = "..\\"
    salida = "documentacion_proyecto.md"
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    print("🔄 Iniciando generación de documentación...")
    print(f"📁 Ruta: {ruta}")
    print(f"💾 Salida: {salida}")
    
    start_time = time.time()
    
    with open(salida, "w", encoding="utf-8") as f:
        # Encabezado del documento
        f.write("# 📚 DOCUMENTACIÓN COMPLETA DEL PROYECTO\n\n")
        f.write(f"**Generado automáticamente:** {timestamp}\n\n")
        f.write("---\n\n")
        
        # 1) SECCIÓN: Estructura del proyecto
        f.write("## 🗂️ Estructura de Carpetas\n\n")
        f.write("A continuación se muestra la estructura completa del proyecto:\n\n")
        
        f.write("```\n")
        arbol_lines = list(draw_tree(
            ruta, 
            show_hidden=False, 
            max_depth=4, 
            use_unicode=True, 
            use_emojis=False
        ))
        for line in arbol_lines:
            f.write(line + "\n")
        f.write("```\n\n")
        
        f.write("---\n\n")
        f.flush()
        
        print("✅ Estructura de carpetas generada")
        
        # 2) SECCIÓN: Código y documentación
        f.write("## 🧩 Análisis de Código\n\n")
        f.write("En esta sección se muestran los archivos más importantes con fragmentos clave y documentación automática.\n\n")
        
        # Configuración optimizada para la documentación
        write_markdown_stream(
            f, ruta,
            show_hidden=False,
            max_depth=3,
            base_level=3,
            files_as_headings=True,      # Cada archivo como heading
            link_files=True,
            allowed_extensions={
                "py", "js", "html", "css", "md", "php", "json", 
                "ts", "jsx", "tsx", "xml", "yaml", "yml", "sql"
            },
            max_file_bytes=150000,
            lang_override={
                "py": "python", 
                "js": "javascript", 
                "ts": "typescript",
                "jsx": "jsx",
                "tsx": "tsx",
                "html": "html", 
                "css": "css",
                "php": "php",
                "sql": "sql",
                "yaml": "yaml",
                "yml": "yaml"
            },
            use_emojis=True,
            escape_html_for_exts={"html", "htm", "xml", "xhtml", "svg"},
            use_ai_doc=True,
            ai_only_when_allowed_ext=True,
            # Configuración optimizada para el contexto del proyecto
            project_ctx_allowed_exts={
                "py", "js", "ts", "html", "css", "md", "php", "json"
            },
            project_ctx_max_file_bytes=35000,
            project_ctx_max_chars=250000,
        )
        
        # 3) SECCIÓN: Información final
        f.write("\n---\n\n")
        f.write("## 📋 Información Técnica\n\n")
        
        total_time = time.time() - start_time
        f.write(f"- **Tiempo de generación:** {total_time:.2f} segundos\n")
        f.write(f"- **Total de archivos analizados:** Todos los archivos de texto en el proyecto\n")
        f.write(f"- **Profundidad máxima:** 3 niveles de carpetas\n")
        f.write(f"- **Documentación IA:** Activada\n")
        f.write(f"- **Fragmentos inteligentes:** Activados\n\n")
        
        f.write("---\n\n")
        f.write("> **Nota:** Esta documentación se genera automáticamente. ")
        f.write("Para ver el código completo de cualquier archivo, abre el archivo directamente desde tu editor.\n")
    
    print(f"✅ Documentación completada en {total_time:.2f} segundos")
    print(f"📄 Archivo guardado: {salida}")
    
    # Estadísticas finales
    try:
        with open(salida, "r", encoding="utf-8") as f:
            contenido = f.read()
            lineas = contenido.count('\n') + 1
            print(f"📊 Estadísticas: {lineas} líneas generadas")
    except:
        pass

def generar_documentacion_rapida():
    """
    Versión rápida para desarrollo - menos profundidad, sin IA
    """
    ruta = "..\\"
    salida = "doc_rapida.md"
    
    print("⚡ Generando documentación rápida...")
    
    with open(salida, "w", encoding="utf-8") as f:
        f.write("# 🚀 DOCUMENTACIÓN RÁPIDA\n\n")
        f.write("> Generada en modo rápido - sin análisis IA\n\n")
        
        f.write("## Estructura\n\n```\n")
        for line in draw_tree(ruta, show_hidden=False, max_depth=2):
            f.write(line + "\n")
        f.write("```\n\n")
        
        # Solo estructura, sin IA
        write_markdown_stream(
            f, ruta,
            show_hidden=False,
            max_depth=2,
            base_level=2,
            files_as_headings=True,
            link_files=False,
            allowed_extensions={"py", "js", "html", "css", "md"},
            max_file_bytes=50000,
            use_ai_doc=False,  # Sin IA para mayor velocidad
            use_emojis=False,
        )
    
    print(f"✅ Documentación rápida guardada: {salida}")

if __name__ == "__main__":
    # Ejecutar documentación completa
    generar_documentacion_completa()
    
    # Opcional: también generar versión rápida
    # generar_documentacion_rapida()
    
    print("\n🎉 ¡Proceso completado!")
    print("💡 Consejo: Abre el archivo .md en Visual Studio Code para mejor visualización")