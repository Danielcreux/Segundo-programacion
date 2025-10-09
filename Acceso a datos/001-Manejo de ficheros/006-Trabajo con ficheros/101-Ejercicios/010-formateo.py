import os

ruta = "C:\\xampp\\htdocs\\Segundo-programacion"

for directorio, subdirectorios, archivos in os.walk(ruta):
    # Calculate the level by counting separators relative to the root
    nivel = directorio.replace(ruta, "").count(os.sep)
    
    print("  "*nivel,directorio+" nivel "+str(nivel))


    for archivo in archivos:
        print((nivel+1)*"  "+archivo)
