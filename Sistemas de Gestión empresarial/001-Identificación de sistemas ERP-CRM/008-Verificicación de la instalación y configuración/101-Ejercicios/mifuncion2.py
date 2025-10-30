import xml.etree.ElementTree as ET
import sqlite3
from flask import request

DB_NAME = "odoo.db"
TABLE_NAME = "interfaz"


def _get_fields_from_xml(root):
    """
    Devuelve lista de tuplas (tipo, nombre) en el orden del XML.
    Tipos esperados en este ejemplo: campotexto, areadetexto
    """
    fields = []
    for nodo in root:
        nombre = nodo.get("nombre")
        if not nombre:
            continue
        if nodo.tag in ("campotexto", "areadetexto"):
            fields.append((nodo.tag, nombre))
    return fields


def _ensure_table(root):
    """
    Crea la tabla 'interfaz' si no existe, con columnas a partir del XML.
    """
    fields = _get_fields_from_xml(root)

    cols_sql = []
    for _, nombre in fields:
        # Todas TEXT para simplicidad; se puede sofisticar por tipo
        cols_sql.append(f'"{nombre}" TEXT')

    create_sql = f'''
        CREATE TABLE IF NOT EXISTS "{TABLE_NAME}" (
            "Identificador" INTEGER PRIMARY KEY AUTOINCREMENT,
            {", ".join(cols_sql)}
        );
    '''

    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute(create_sql)
        con.commit()


def miInterfaz(destino_xml: str):
    """
    - GET: renderiza formulario basado en XML.
    - POST: inserta datos recibidos y confirma guardado.
    """
    tree = ET.parse(destino_xml)
    root = tree.getroot()
    fields = _get_fields_from_xml(root)
    _ensure_table(root)

    if request.method == "POST":
        # Recoger datos en el orden del XML
        nombres = [nombre for _, nombre in fields]
        valores = [request.form.get(nombre, "") for nombre in nombres]

        placeholders = ", ".join(["?"] * len(nombres))
        columnas = ", ".join([f'"{n}"' for n in nombres])
        insert_sql = f'INSERT INTO "{TABLE_NAME}" ({columnas}) VALUES ({placeholders})'

        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute(insert_sql, valores)
            con.commit()

        return (
            "<!doctype html>"
            "<html><head><meta charset='utf-8'><title>Guardado</title>"
            "<style>body{font-family:system-ui;margin:2rem} a{display:inline-block;margin-top:1rem}</style>"
            "</head><body>"
            "<h1>✅ Datos guardados correctamente</h1>"
            "<p><a href='/'>Volver al formulario</a> | <a href='/tabla'>Ver tabla</a></p>"
            "</body></html>"
        )

    # GET → Render del formulario
    inputs_html = []
    for tipo, nombre in fields:
        label = f"<label for='{nombre}'>{nombre}</label>"
        if tipo == "campotexto":
            control = f"<input id='{nombre}' type='text' name='{nombre}' placeholder='{nombre}'>"
        elif tipo == "areadetexto":
            control = f"<textarea id='{nombre}' name='{nombre}' rows='5' placeholder='{nombre}'></textarea>"
        else:
            # Por si se añaden más tipos en el futuro
            control = f"<input id='{nombre}' type='text' name='{nombre}' placeholder='{nombre}'>"

        inputs_html.append(f"<div class='campo'>{label}{control}</div>")

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Formulario</title>
        <style>
          :root {{ --gap: 12px; }}
          body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
          form {{ max-width: 720px; display:grid; gap: var(--gap); }}
          .campo {{ display:flex; flex-direction:column; gap:6px; }}
          input, textarea {{
            padding: 10px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;
          }}
          button {{
            padding: 10px 16px; border: 0; border-radius: 8px; font-size: 16px; cursor: pointer;
          }}
          .actions {{ display:flex; gap: var(--gap); }}
        </style>
      </head>
      <body>
        <h1>Formulario</h1>
        <form method="post" action="/">
          {"".join(inputs_html)}
          <div class="actions">
            <button type="submit">Enviar</button>
            <a href="/tabla">Ver tabla</a>
          </div>
        </form>
      </body>
    </html>
    """
    return html


def tablaInterfaz(destino_xml: str):
    """
    Renderiza una tabla HTML con todos los registros de la base de datos,
    usando las columnas definidas por el XML (mismo mapeo campos ⇄ columnas).
    """
    tree = ET.parse(destino_xml)
    root = tree.getroot()
    fields = _get_fields_from_xml(root)
    _ensure_table(root)

    headers = ["Identificador"] + [nombre for _, nombre in fields]

    # Query de todos los registros (ordenados por Identificador desc)
    select_cols = ", ".join([f'"{TABLE_NAME}"."Identificador"'] + [f'"{TABLE_NAME}"."{n}"' for _, n in fields])
    select_sql = f'SELECT {select_cols} FROM "{TABLE_NAME}" ORDER BY "Identificador" DESC'

    rows = []
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute(select_sql)
        rows = cur.fetchall()

    # Construcción HTML de tabla
    thead = "".join([f"<th>{h}</th>" for h in headers])
    trs = []
    for row in rows:
        tds = "".join([f"<td>{(c if c is not None else '')}</td>" for c in row])
        trs.append(f"<tr>{tds}</tr>")

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Tabla de registros</title>
        <style>
          body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
          table {{ border-collapse: collapse; width: 100%; max-width: 1000px; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; }}
          th {{ background: #f5f5f5; text-align: left; }}
          caption {{ text-align:left; font-weight:600; margin-bottom: .5rem; }}
          .actions a {{ display:inline-block; margin-right: .75rem; }}
        </style>
      </head>
      <body>
        <h1>Registros</h1>
        <div class="actions">
          <a href="/">← Volver al formulario</a>
        </div>
        <table>
          <caption>Total: {len(rows)} registro(s)</caption>
          <thead><tr>{thead}</tr></thead>
          <tbody>
            {"".join(trs) if trs else "<tr><td colspan='{len(headers)}'>Sin datos</td></tr>"}
          </tbody>
        </table>
      </body>
    </html>
    """
    return html
