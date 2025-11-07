@echo off
echo Iniciando Micro ChatGPT...

:: Activar entorno virtual
call venv\Scripts\activate

:: Ejecutar aplicación
cd /d "C:\xampp\htdocs\Segundo-programacion\Desarrollo de interfaces\002-Generación de interfaces naturales de usuario\001-Herramientas para el aprendizaje automático\101-Ejercicios\microchatgpt\backend"
py "app.py"

pause