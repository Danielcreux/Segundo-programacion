import os

class YourSQL:
  carpeta_bd = "db"
  base_actual = ""

  @staticmethod
  def peticion(peticion):
    if peticion == "SHOW DATABASES;":
      carpetas = os.listdir(YourSQL.carpeta_bd)
      for carpeta in carpetas:
        print(carpeta)
    elif "USE" in peticion:
      YourSQL.base_actual = peticion.split(" ")[1].split(";")[0]
    elif peticion == "SHOW TABLES;":
      tablas = os.listdir(YourSQL.carpeta_bd+"/"+YourSQL.base_actual)
      for tabla in tablas:
        print(tabla)
    elif "INSERT" in peticion:
      import re, csv, io

      # 1) Regex para capturar tabla, columnas (opcionales) y bloque VALUES
      patron = re.compile(
          r"^\s*INSERT\s+INTO\s+([A-Za-z_][\w$]*)\s*"
          r"(?:\(([^)]+)\))?\s*"
          r"VALUES\s*(.+?)\s*;?\s*$",
          re.IGNORECASE | re.DOTALL
      )
      m = patron.match(peticion)
      if not m:
          raise ValueError("INSERT no reconocido.")

      tabla, columnas_str, values_blob = m.groups()

      # 2) Ruta CSV
      ruta_base = os.path.join(YourSQL.carpeta_bd, YourSQL.base_actual)
      os.makedirs(ruta_base, exist_ok=True)
      path_csv = os.path.join(ruta_base, f"{tabla}.csv")

      # 3) Columnas (si vienen explícitas)
      columnas = None
      if columnas_str:
          columnas = [c.strip().strip("`") for c in columnas_str.split(",")]

      # 4) Separar tuplas de VALUES respetando comillas simples
      def split_tuplas(s: str):
          res, buf = [], []
          en_cadena = False
          nivel = 0
          prev = ''
          for ch in s.strip():
              if ch == "'" and prev != '\\':
                  en_cadena = not en_cadena
                  buf.append(ch)
              elif not en_cadena and ch == '(':
                  if nivel > 0:
                      buf.append(ch)
                  nivel += 1
              elif not en_cadena and ch == ')':
                  nivel -= 1
                  if nivel == 0:
                      res.append(''.join(buf).strip())
                      buf = []
                  else:
                      buf.append(ch)
              elif not en_cadena and nivel == 0 and ch == ',':
                  # separador entre tuplas
                  pass
              else:
                  buf.append(ch)
              prev = ch
          return res

      tuplas = split_tuplas(values_blob)

      # 5) Parsear cada tupla en lista de valores usando csv.reader (quote="'", escape="\\")
      filas = []
      for t in tuplas:
          reader = csv.reader(
              io.StringIO(t),
              delimiter=',',
              quotechar="'",
              escapechar='\\',
              skipinitialspace=True
          )
          vals = next(reader)
          filas.append([None if v.strip().upper() == "NULL" else v.strip() for v in vals])

      # 6) Si no hay columnas: usar cabecera existente o generar c1..cn
      if columnas is None:
          if os.path.exists(path_csv):
              with open(path_csv, newline='', encoding='utf-8') as f:
                  r = csv.reader(f)
                  columnas = next(r, None)
          if not columnas:
              columnas = [f"c{i}" for i in range(1, len(filas[0]) + 1)]

      # 7) Escribir/añadir CSV
      existe = os.path.exists(path_csv)
      with open(path_csv, 'a', newline='', encoding='utf-8') as f:
          writer = csv.DictWriter(f, fieldnames=list(columnas))
          if not existe:
              writer.writeheader()
          for vals in filas:
              writer.writerow({col: (vals[i] if i < len(vals) else "") for i, col in enumerate(columnas)})

      print(f"{len(filas)} fila(s) insertadas en {tabla}")

            
YourSQL.peticion("USE accesoadatos;")
YourSQL.peticion("SHOW TABLES;")
YourSQL.peticion("INSERT INTO clientes (id, nombre, email, activo) VALUES (1, 'Ana', 'ana@example.com', TRUE), (2, 'Luis O\\'Connor', NULL, FALSE);")

