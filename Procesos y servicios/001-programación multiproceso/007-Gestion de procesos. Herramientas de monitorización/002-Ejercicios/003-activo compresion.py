import os
import zipfile

carpeta = "C:\\Users\\Valentina\\Desktop\\muchovideos"

archivos = os.listdir(carpeta)

for archivo in archivos:
  archivozip = zipfile.ZipFile(os.path.join(carpeta,archivo+".zip"), 'w', zipfile.ZIP_DEFLATED)
  archivozip.write(os.path.join(carpeta,archivo))
  