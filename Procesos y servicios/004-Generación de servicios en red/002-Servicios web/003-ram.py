# ram_monitor.py
import psutil
import csv
from datetime import datetime
import os

# File to store RAM usage history
CSV_FILE = 'ram_usage_history.csv'

def get_ram_usage():
    """Returns RAM usage percentage and total RAM in GB."""
    ram = psutil.virtual_memory()
    return ram.percent, round(ram.total / (1024 ** 3), 2)  # Total in GB

def save_ram_usage(ram_percent, ram_total_gb):
    """Saves RAM usage and current date to CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'ram_pressure_percent', 'ram_total_gb'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ram_percent, ram_total_gb])

if __name__ == '__main__':
    ram_percent, ram_total_gb = get_ram_usage()
    save_ram_usage(ram_percent, ram_total_gb)
    print(f"Saved RAM usage: {ram_percent}%, Total: {ram_total_gb} GB")

