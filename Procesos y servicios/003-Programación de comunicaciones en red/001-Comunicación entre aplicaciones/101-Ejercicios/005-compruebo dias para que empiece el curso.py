import requests
import csv
from io import StringIO

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1whDcBEU6BnFwlVZHICoMdkGU_au42HiWaPoNschUDr2ri7baRZDjWofnMlxnQKk35raLVm9rIKQk/pub?output=csv"

# Descargar CSV
resp = requests.get(url)
resp.raise_for_status()

# Convertir a diccionarios usando la primera fila como keys
f = StringIO(resp.text)
reader = csv.DictReader(f)

rows = list(reader)

# Mostrar cada fila como diccionario
for r in rows:
    print("Nombre del alumno: "+r['Nombre completo'])
    print("Curso: "+r['Curso'])
    print("Fecha: "+r['Fecha de inicio'])
    print("######################")

