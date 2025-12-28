# disk_io_monitor_simple.py
import psutil
import csv
from datetime import datetime
import os

CSV_FILE = 'disk_io_history.csv'

def get_disk_io():
    """Returns disk I/O stats with safe attribute access."""
    disks = psutil.disk_io_counters(perdisk=True)
    data = []
    
    if not disks:
        return data
    
    for disk_name, io in disks.items():
        # Usar getattr para manejar atributos que pueden no existir
        disk_info = {
            'disk': disk_name,
            'read_bytes': getattr(io, 'read_bytes', 0),
            'write_bytes': getattr(io, 'write_bytes', 0),
            'read_count': getattr(io, 'read_count', 0),
            'write_count': getattr(io, 'write_count', 0),
            'read_time': getattr(io, 'read_time', 0),
            'write_time': getattr(io, 'write_time', 0),
        }
        
        # Intentar obtener busy_time si existe
        if hasattr(io, 'busy_time'):
            disk_info['busy_time'] = io.busy_time
        
        data.append(disk_info)
    
    return data

def save_disk_io(data):
    """Saves disk I/O stats to CSV."""
    if not data:
        print("No data to save")
        return
    
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as f:
        # Usar todos los campos disponibles en el primer registro
        fieldnames = ['timestamp'] + list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for entry in data:
            row = entry.copy()
            row['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(row)
    
    print(f"Saved data for {len(data)} disks to {CSV_FILE}")

def main():
    data = get_disk_io()
    
    if data:
        print(f"Found {len(data)} disk(s):")
        for disk in data:
            print(f"\nDisk: {disk['disk']}")
            print(f"  Read: {disk['read_bytes']:,} bytes ({disk['read_count']} ops)")
            print(f"  Write: {disk['write_bytes']:,} bytes ({disk['write_count']} ops)")
            
            if 'busy_time' in disk:
                print(f"  Busy time: {disk['busy_time']} ms")
        
        save_disk_io(data)
    else:
        print("No disk I/O data available")

if __name__ == '__main__':
    main()