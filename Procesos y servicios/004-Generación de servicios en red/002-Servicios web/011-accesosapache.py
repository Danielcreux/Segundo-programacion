# apache_request_rate_monitor.py
import csv
from datetime import datetime, timedelta
import re
import os

# Path to Apache2 access log
ACCESS_LOG = '/var/log/apache2/access.log'
# File to store request rate history
CSV_FILE = 'apache_request_rate_history.csv'

def parse_apache_log_line(line):
    """Parses a line from the Apache2 access log and returns the timestamp."""
    # Example log format: 127.0.0.1 - - [25/Nov/2025:12:00:00 +0100] "GET / HTTP/1.1" 200 1234
    match = re.search(r'\[([^\]]+)\]', line)
    if match:
        timestamp_str = match.group(1)
        return datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
    return None

def count_requests_per_minute(log_file, minutes=1):
    """Counts requests per minute from the Apache2 access log."""
    request_counts = {}
    current_time = datetime.now()
    time_window = timedelta(minutes=minutes)

    with open(log_file, 'r') as f:
        for line in f:
            timestamp = parse_apache_log_line(line)
            if timestamp and (current_time - timestamp) <= time_window:
                minute_key = timestamp.strftime('%Y-%m-%d %H:%M')
                request_counts[minute_key] = request_counts.get(minute_key, 0) + 1

    return request_counts

def save_request_rate(request_counts):
    """Saves request rate data to CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'requests_per_minute'])
        for minute, count in request_counts.items():
            writer.writerow([minute, count])

if __name__ == '__main__':
    request_counts = count_requests_per_minute(ACCESS_LOG)
    save_request_rate(request_counts)
    print(f"Saved request rate data for {len(request_counts)} minutes.")

