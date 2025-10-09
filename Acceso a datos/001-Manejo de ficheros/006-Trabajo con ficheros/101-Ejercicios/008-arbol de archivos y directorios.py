import os

ruta = "/var/www/html/dam2526"

for directorio, subdirectorios, archivos in os.walk(ruta):
    # Calculate the level by counting separators relative to the root
    nivel = directorio.replace(ruta, "").count(os.sep)
    print(f"Directorio: {directorio} (nivel {nivel})")

    for sub in subdirectorios:
        print(f"{'  ' * (nivel+1)}Subdirectorio: {sub} (nivel {nivel+1})")

    for archivo in archivos:
        print(f"{'  ' * (nivel+1)}Archivo: {archivo} (nivel {nivel+1})")
