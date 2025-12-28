import requests
import csv
from io import StringIO
from datetime import date, datetime

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1whDcBEU6BnFwlVZHICoMdkGU_au42HiWaPoNschUDr2ri7baRZDjWofnMlxnQKk35raLVm9rIKQk/pub?output=csv"

# Descargar CSV
resp = requests.get(url)
resp.raise_for_status()

# Convertir a diccionarios usando la primera fila como keys
f = StringIO(resp.text)
reader = csv.DictReader(f)

rows = list(reader)

# Cargar variables de entorno SOLO una vez
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

hoy = date.today()

for r in rows:
    print("Nombre del alumno: " + r['Nombre completo'])
    print("Curso: " + r['Curso'])
    print("Fecha: " + r['Fecha de inicio'])

    fecha_str = r['Fecha de inicio']
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

    diff = (hoy - fecha).days  # si el curso es dentro de 3 días, diff será -3

    if diff == -3:
        print("Faltan 3 días para que empiece el curso")

        nombre = r['Nombre completo']
        curso = r['Curso']

        # --- HTML bonito con CSS inline ---
        html_body = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Tu curso empieza en 3 días</title>
  <style>
    /* Estilos básicos (la mayoría de clientes los respetan) */
    body {{
      margin: 0;
      padding: 0;
      background-color: #0f172a;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .wrapper {{
      width: 100%;
      padding: 32px 0;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background: #020617;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 24px 60px rgba(15,23,42,0.8);
      border: 1px solid rgba(148,163,184,0.25);
    }}
    .header {{
      padding: 24px 32px 16px;
      background: radial-gradient(circle at top left, #22c55e, #0ea5e9 40%, #0b1120);
      color: #e5e7eb;
    }}
    .logo {{
      font-size: 12px;
      letter-spacing: .25em;
      text-transform: uppercase;
      opacity: 0.9;
    }}
    .title {{
      margin-top: 16px;
      font-size: 24px;
      font-weight: 700;
      line-height: 1.3;
    }}
    .badge {{
      display: inline-block;
      margin-top: 16px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .15em;
      background: rgba(15,23,42,0.7);
      border: 1px solid rgba(148,163,184,0.6);
      color: #e5e7eb;
    }}
    .content {{
      padding: 24px 32px 28px;
      color: #e5e7eb;
    }}
    .hello {{
      font-size: 15px;
      margin-bottom: 12px;
    }}
    .highlight-box {{
      margin: 18px 0 20px;
      padding: 14px 16px;
      border-radius: 14px;
      background: rgba(15,23,42,0.9);
      border: 1px solid rgba(148,163,184,0.35);
    }}
    .highlight-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .16em;
      color: #9ca3af;
      margin-bottom: 6px;
    }}
    .highlight-value {{
      font-size: 15px;
      font-weight: 600;
      color: #e5e7eb;
    }}
    .date-row {{
      display: flex;
      gap: 10px;
      margin-top: 8px;
      font-size: 12px;
      color: #9ca3af;
    }}
    .pill {{
      padding: 4px 8px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.4);
      background: rgba(15,23,42,0.85);
    }}
    .cta {{
      margin-top: 18px;
      text-align: center;
    }}
    .cta-button {{
      display: inline-block;
      padding: 10px 20px;
      border-radius: 999px;
      background: linear-gradient(90deg, #22c55e, #0ea5e9);
      color: #020617 !important;
      font-weight: 600;
      font-size: 14px;
      text-decoration: none;
      box-shadow: 0 14px 35px rgba(34,197,94,0.35);
    }}
    .cta-note {{
      margin-top: 10px;
      font-size: 12px;
      color: #9ca3af;
    }}
    .footer {{
      padding: 16px 32px 20px;
      font-size: 11px;
      color: #6b7280;
      background: #020617;
      border-top: 1px solid rgba(31,41,55,0.8);
    }}
    .footer small {{
      display: block;
      margin-top: 4px;
    }}

    @media (max-width: 640px) {{
      .container {{
        border-radius: 0;
      }}
      .header, .content, .footer {{
        padding-left: 18px;
        padding-right: 18px;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      <div class="header">
        <div class="logo">CAMPUS · CAPITOL FORMACIÓN</div>
        <div class="title">Tu curso empieza en 3 días 🎓</div>
        <div class="badge">Cuenta atrás para empezar</div>
      </div>

      <div class="content">
        <p class="hello">Hola <strong>{nombre}</strong>,</p>
        <p>
          Solo queríamos recordarte que tu curso está a punto de comenzar.
          Es un buen momento para revisar tu correo, acceder al campus y asegurarte
          de que puedes iniciar sesión sin problemas.
        </p>

        <div class="highlight-box">
          <div class="highlight-label">Curso</div>
          <div class="highlight-value">{curso}</div>

          <div class="date-row">
            <div class="pill">Fecha de inicio: {fecha_str}</div>
            <div class="pill">Empieza en 3 días</div>
          </div>
        </div>

        <p>
          El día de inicio tendrás acceso al contenido, actividades y recursos
          del curso. Si tienes cualquier problema de acceso o duda, puedes
          responder a este correo y te ayudaremos.
        </p>

        <div class="cta">
          <a href="https://campus.capitolformacion.com" class="cta-button">
            Ir al campus virtual
          </a>
          <div class="cta-note">
            Consejo: añade este correo a tus contactos para no perder futuras notificaciones.
          </div>
        </div>
      </div>

      <div class="footer">
        Este es un aviso automático de inicio de curso.
        <small>Si ya has recibido este recordatorio o ya has accedido al campus, puedes ignorar este mensaje.</small>
      </div>
    </div>
  </div>
</body>
</html>
"""

        # Crear mensaje MIME como HTML
        msg = MIMEText(html_body, "html", "utf-8")
        msg["Subject"] = f"Tu curso de {curso} empieza en 3 días"
        msg["From"] = SMTP_USER
        msg["To"] = "jocarsa2@gmail.com"  # o el correo del alumno si lo añades al CSV

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())

        print("Correo HTML enviado ✅")
        print("######################")

