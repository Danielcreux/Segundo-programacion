# disk_monitor.py
import psutil
import csv
from datetime import datetime
import os

# File to store disk usage history
CSV_FILE = 'disk_usage_history.csv'

def get_disk_usage():
    """Returns disk usage percentage, total, and free space in GB for the root partition."""
    disk = psutil.disk_usage('/')
    total_gb = round(disk.total / (1024 ** 3), 2)
    free_gb = round(disk.free / (1024 ** 3), 2)
    return disk.percent, total_gb, free_gb

def save_disk_usage(percent, total_gb, free_gb):
    """Saves disk usage and current date to CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'disk_pressure_percent', 'disk_total_gb', 'disk_free_gb'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), percent, total_gb, free_gb])

if __name__ == '__main__':
    percent, total_gb, free_gb = get_disk_usage()
    save_disk_usage(percent, total_gb, free_gb)
    print(f"Saved disk usage: {percent}%, Total: {total_gb} GB, Free: {free_gb} GB")

