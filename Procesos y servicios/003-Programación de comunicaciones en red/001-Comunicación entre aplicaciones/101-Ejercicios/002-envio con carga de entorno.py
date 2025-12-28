import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()  # carga .env automáticamente

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

msg = MIMEText("Hola desde Python con variables ocultas 😎")
msg["Subject"] = "Test"
msg["From"] = SMTP_USER
msg["To"] = "jocarsa2@gmail.com"

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, msg["To"], msg.as_string())

