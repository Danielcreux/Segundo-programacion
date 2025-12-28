# bandwidth_monitor.py
import psutil
import csv
from datetime import datetime
import os

# File to store bandwidth usage history
CSV_FILE = 'bandwidth_usage_history.csv'

def get_bandwidth_usage():
    """Returns bandwidth usage stats: bytes sent/received for each interface."""
    net_io = psutil.net_io_counters(pernic=True)
    data = []
    for iface, io in net_io.items():
        data.append({
            'interface': iface,
            'bytes_sent': io.bytes_sent,
            'bytes_recv': io.bytes_recv,
            'packets_sent': io.packets_sent,
            'packets_recv': io.packets_recv
        })
    return data

def save_bandwidth_usage(data):
    """Saves bandwidth usage stats and current date to CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'date', 'interface', 'bytes_sent',
                'bytes_recv', 'packets_sent', 'packets_recv'
            ])
        for entry in data:
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                entry['interface'],
                entry['bytes_sent'],
                entry['bytes_recv'],
                entry['packets_sent'],
                entry['packets_recv']
            ])

if __name__ == '__main__':
    data = get_bandwidth_usage()
    save_bandwidth_usage(data)
    print(f"Saved bandwidth usage data for {len(data)} interfaces.")

