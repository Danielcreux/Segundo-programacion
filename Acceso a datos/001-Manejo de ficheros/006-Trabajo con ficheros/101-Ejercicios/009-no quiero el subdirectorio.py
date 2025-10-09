import os

ruta = "/var/www/html/dam2526"

for directorio, subdirectorios, archivos in os.walk(ruta):
    # Calculate the level by counting separators relative to the root
    nivel = directorio.replace(ruta, "").count(os.sep)
    
    print(" "*nivel,directorio+" nivel "+str(nivel))


    for archivo in archivos:
        print(f"{'  ' * (nivel+1)}Archivo: {archivo} (nivel {nivel+1})")
