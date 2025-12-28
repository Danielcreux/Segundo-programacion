import requests
import csv
from io import StringIO
from datetime import date, datetime

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
    fecha_str = r['Fecha de inicio']  # tu fecha
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

    hoy = date.today()
    diff = (hoy - fecha).days
    if diff == -3:
      print("Faltan 3 dias para que empiece el curso")
    print("######################")

