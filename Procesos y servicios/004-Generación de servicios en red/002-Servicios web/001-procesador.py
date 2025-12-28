# cpu_monitor.py
import psutil
import csv
from datetime import datetime
import os

# File to store CPU usage history
CSV_FILE = 'cpu_usage_history.csv'

def get_cpu_usage():
    """Returns current CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

def save_cpu_usage(cpu_usage):
    """Saves CPU usage and current date to CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'cpu_pressure'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cpu_usage])

if __name__ == '__main__':
    cpu_usage = get_cpu_usage()
    save_cpu_usage(cpu_usage)
    print(f"Saved CPU usage: {cpu_usage}%")

