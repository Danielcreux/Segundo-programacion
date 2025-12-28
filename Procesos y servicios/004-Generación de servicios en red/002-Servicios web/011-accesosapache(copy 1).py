# 011-accesosapache.py
import os
import re
from datetime import datetime
from collections import defaultdict
import psutil

# Rutas para XAMPP en Windows
XAMPP_DIR = r"C:\xampp"
APACHE_LOG_DIR = os.path.join(XAMPP_DIR, "apache", "logs")
ACCESS_LOG = os.path.join(APACHE_LOG_DIR, "access.log")
ERROR_LOG = os.path.join(APACHE_LOG_DIR, "error.log")

def find_apache_logs():
    """Busca archivos de log de Apache en diferentes ubicaciones posibles."""
    possible_paths = [
        # XAMPP en Windows
        r"C:\xampp\apache\logs\access.log",
        r"C:\xampp\apache\logs\access_log.txt",
        r"C:\Program Files\xampp\apache\logs\access.log",
        
        # Apache standalone en Windows
        r"C:\Apache24\logs\access.log",
        r"C:\Apache\logs\access.log",
        
        # Linux paths (por si acaso)
        "/var/log/apache2/access.log",
        "/var/log/apache/access.log",
        "/var/log/httpd/access_log",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Log encontrado: {path}")
            return path
    
    print("✗ No se encontró el archivo access.log")
    print("Buscando archivos de log en el sistema...")
    
    # Buscar archivos que contengan 'access' en el directorio de XAMPP
    if os.path.exists(XAMPP_DIR):
        for root, dirs, files in os.walk(XAMPP_DIR):
            for file in files:
                if 'access' in file.lower() and file.endswith(('.log', '.txt')):
                    full_path = os.path.join(root, file)
                    print(f"  Posible log: {full_path}")
    
    return None

def count_requests_per_minute(log_file):
    """Cuenta las solicitudes por minuto en el archivo de log."""
    if not log_file or not os.path.exists(log_file):
        print(f"Archivo no encontrado: {log_file}")
        return {}
    
    request_counts = defaultdict(int)
    
    try:
        # Patrón para extraer timestamp de Apache logs
        # Formato común: [10/Oct/2000:13:55:36 -0700]
        pattern = r'\[(\d{2}/\w{3}/\d{4}):(\d{2}:\d{2}:\d{2})'
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    date_str, time_str = match.groups()
                    # Extraer solo hora y minuto
                    hour_minute = time_str[:5]  # HH:MM
                    request_counts[hour_minute] += 1
        
        return dict(request_counts)
    
    except Exception as e:
        print(f"Error leyendo el log: {e}")
        return {}

def analyze_apache_status():
    """Analiza el estado del servidor Apache."""
    print("=" * 60)
    print("ANÁLISIS DE SERVIDOR APACHE")
    print("=" * 60)
    
    # 1. Verificar procesos Apache
    print("\n1. PROCESOS APACHE:")
    apache_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            if 'httpd' in name or 'apache' in name or name.endswith('.exe') and 'apache' in name:
                apache_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if apache_processes:
        print(f"   ✓ Apache está corriendo ({len(apache_processes)} procesos)")
        for proc in apache_processes[:3]:  # Mostrar solo los primeros 3
            print(f"      PID {proc['pid']}: {proc['name']}")
    else:
        print("   ✗ Apache NO está corriendo")
    
    # 2. Verificar puertos
    print("\n2. PUERTOS EN USO:")
    ports_to_check = [80, 443, 8080]
    
    for port in ports_to_check:
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    print(f"   ✓ Puerto {port} está en uso por PID {conn.pid}")
                    break
            else:
                print(f"   ✗ Puerto {port} no está en uso")
        except:
            print(f"   ? No se pudo verificar puerto {port}")
    
    # 3. Buscar y analizar logs
    print("\n3. ARCHIVOS DE LOG:")
    log_file = find_apache_logs()
    
    if log_file:
        # Mostrar información del archivo
        file_size = os.path.getsize(log_file)
        file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        
        print(f"   Archivo: {log_file}")
        print(f"   Tamaño: {file_size / 1024:.2f} KB")
        print(f"   Última modificación: {file_time}")
        
        # Contar líneas (solo las últimas 1000 para no saturar)
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
                print(f"   Total de líneas: {total_lines}")
        except:
            print("   No se pudo contar líneas")
        
        # Analizar últimas entradas
        print("\n   ÚLTIMAS 5 SOLICITUDES:")
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    # Simplificar para mostrar
                    parts = line.split()
                    if len(parts) > 3:
                        ip = parts[0]
                        date = parts[3] + " " + parts[4] if len(parts) > 4 else ""
                        request = parts[5] + " " + parts[6] if len(parts) > 6 else ""
                        print(f"      {ip} - {date} - {request[:50]}...")
        except:
            print("      No se pudieron leer las últimas solicitudes")
    
    # 4. Verificar servicios de Windows (si aplica)
    print("\n4. SERVICIOS WINDOWS:")
    try:
        import win32service  # Solo disponible en Windows
        
        services = ['Apache2.4', 'Apache', 'httpd']
        for service in services:
            try:
                # Intentar verificar el servicio
                # (Esto es simplificado, necesitarías pywin32 instalado)
                print(f"   {service}: Disponible")
            except:
                print(f"   {service}: No encontrado")
    except ImportError:
        print("   (Info: pywin32 no instalado para verificación de servicios)")

def monitor_realtime_requests(log_file, duration=30):
    """Monitoreo en tiempo real de solicitudes."""
    if not log_file or not os.path.exists(log_file):
        print("No se puede monitorear: archivo de log no encontrado")
        return
    
    print(f"\nMONITOREO EN TIEMPO REAL ({duration} segundos)")
    print("-" * 40)
    
    import time
    
    # Obtener posición inicial del archivo
    file_size = os.path.getsize(log_file)
    
    start_time = time.time()
    request_count = 0
    
    try:
        while time.time() - start_time < duration:
            current_size = os.path.getsize(log_file)
            
            if current_size > file_size:
                # Leer nuevas líneas
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(file_size)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        request_count += 1
                        parts = line.split()
                        if len(parts) > 0:
                            ip = parts[0]
                            timestamp = parts[3] + " " + parts[4] if len(parts) > 4 else ""
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] {ip} - {timestamp}")
                    
                    file_size = current_size
            
            time.sleep(1)  # Esperar 1 segundo entre verificaciones
    
    except KeyboardInterrupt:
        print("\nMonitoreo interrumpido por el usuario")
    
    print(f"\nTotal de solicitudes durante el monitoreo: {request_count}")

def main():
    """Función principal."""
    print("ANALIZADOR DE ACCESOS APACHE - XAMPP/WINDOWS")
    print("=" * 60)
    
    # Primero verificar si XAMPP está instalado
    if not os.path.exists(XAMPP_DIR):
        print(f"XAMPP no encontrado en: {XAMPP_DIR}")
        print("Por favor, ajusta la ruta XAMPP_DIR en el script.")
    
    # Menú interactivo
    while True:
        print("\nOPCIONES:")
        print("  1. Analizar estado de Apache")
        print("  2. Monitorear acceso en tiempo real")
        print("  3. Buscar archivos de log")
        print("  4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            analyze_apache_status()
        elif choice == "2":
            log_file = find_apache_logs()
            if log_file:
                duration = input("Duración en segundos (default 30): ").strip()
                try:
                    duration = int(duration) if duration else 30
                    monitor_realtime_requests(log_file, duration)
                except ValueError:
                    print("Duración inválida, usando 30 segundos")
                    monitor_realtime_requests(log_file, 30)
            else:
                print("Primero encuentra un archivo de log válido")
        elif choice == "3":
            log_file = find_apache_logs()
            if log_file:
                print(f"\nArchivo de log principal: {log_file}")
        elif choice == "4":
            print("Saliendo...")
            break
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()