import requests
import os
import hashlib
from datetime import datetime
from urllib.parse import urlparse

url = "https://tameformacion.com/"
output_folder = "paginas_html"

# Create folder if it does not exist
os.makedirs(output_folder, exist_ok=True)

def get_filename_from_url(url: str) -> str:
    """Returns a filename based on the URL path, if possible."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    # If URL ends with a filename (e.g., page.php, index.html)
    if "." in path:
        return path

    # If URL has a path but no extension (e.g., /contact/)
    if path:
        return path + ".html"

    # If nothing can be extracted, return empty string
    return ""


def generate_hash_filename(url: str) -> str:
    """Generates filename using hash + datetime."""
    sha1 = hashlib.sha1(url.encode()).hexdigest()[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{sha1}_{timestamp}.html"


try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    html_content = response.text

    # Determine filename
    filename = get_filename_from_url(url)
    if not filename:
        filename = generate_hash_filename(url)

    filepath = os.path.join(output_folder, filename)

    # Save HTML
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML saved to: {filepath}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

