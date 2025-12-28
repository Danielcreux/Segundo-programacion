# disk_io_monitor.py
import psutil
import csv
from datetime import datetime
import os

# File to store disk I/O history
CSV_FILE = 'disk_io_history.csv'

def get_disk_io():
    """Returns disk I/O stats: read/write bytes, operations, and latency."""
    disks = psutil.disk_io_counters(perdisk=True)
    data = []
    for disk_name, io in disks.items():
        data.append({
            'disk': disk_name,
            'read_bytes': io.read_bytes,
            'write_bytes': io.write_bytes,
            'read_ops': io.read_count,
            'write_ops': io.write_count,
            'read_time_ms': io.read_time,
            'write_time_ms': io.write_time,
            'busy_time_ms': io.busy_time
        })
    return data

def save_disk_io(data):
    """Saves disk I/O stats and current date to CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'date', 'disk', 'read_bytes', 'write_bytes',
                'read_ops', 'write_ops', 'read_time_ms',
                'write_time_ms', 'busy_time_ms'
            ])
        for entry in data:
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                entry['disk'], entry['read_bytes'], entry['write_bytes'],
                entry['read_ops'], entry['write_ops'],
                entry['read_time_ms'], entry['write_time_ms'],
                entry['busy_time_ms']
            ])

if __name__ == '__main__':
    data = get_disk_io()
    save_disk_io(data)
    print(f"Saved disk I/O data for {len(data)} disks.")

