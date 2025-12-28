# server_monitor_simple.py
import psutil
import csv
from datetime import datetime
import os
import sys

# Config
CSV_DIR = 'monitor_data'
os.makedirs(CSV_DIR, exist_ok=True)

def save_to_csv(filename, headers, data):
    """Guardar datos en CSV."""
    filepath = os.path.join(CSV_DIR, filename)
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(data)

def monitor_all():
    """Monitorear todo de forma segura."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # CPU
    try:
        cpu = psutil.cpu_percent(interval=1)
        save_to_csv('cpu.csv', ['date', 'usage'], [timestamp, cpu])
    except:
        pass
    
    # RAM
    try:
        ram = psutil.virtual_memory()
        save_to_csv('ram.csv', ['date', 'percent', 'total_gb', 'used_gb'],
                   [timestamp, ram.percent, 
                    round(ram.total/(1024**3),2), round(ram.used/(1024**3),2)])
    except:
        pass
    
    # Disk I/O (Windows compatible)
    try:
        disks = psutil.disk_io_counters(perdisk=True)
        for disk, io in disks.items():
            # Solo usar atributos que siempre existen
            save_to_csv(f'disk_{disk}.csv',
                       ['date', 'read_bytes', 'write_bytes', 'read_ops', 'write_ops'],
                       [timestamp, io.read_bytes, io.write_bytes, 
                        io.read_count, io.write_count])
    except:
        pass
    
    # Disk Usage
    try:
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                save_to_csv(f'usage_{part.device.replace(":", "")}.csv',
                           ['date', 'percent', 'total_gb', 'free_gb'],
                           [timestamp, usage.percent,
                            round(usage.total/(1024**3),2), round(usage.free/(1024**3),2)])
            except:
                continue
    except:
        pass
    
    # Network
    try:
        net = psutil.net_io_counters()
        save_to_csv('network.csv',
                   ['date', 'sent_mb', 'recv_mb', 'packets_sent', 'packets_recv'],
                   [timestamp,
                    round(net.bytes_sent/(1024**2),2),
                    round(net.bytes_recv/(1024**2),2),
                    net.packets_sent, net.packets_recv])
    except:
        pass
    
    print(f"Monitoring completed at {timestamp}")

if __name__ == '__main__':
    monitor_all()