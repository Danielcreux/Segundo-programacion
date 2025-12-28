import requests
import csv
from io import StringIO

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1whDcBEU6BnFwlVZHICoMdkGU_au42HiWaPoNschUDr2ri7baRZDjWofnMlxnQKk35raLVm9rIKQk/pub?output=csv"

# Descarga del CSV
resp = requests.get(url)
resp.raise_for_status()   # por si algo va mal

# Convertimos texto → CSV
data = list(csv.reader(StringIO(resp.text)))

# Mostrar por consola
for row in data:
    print(row)

