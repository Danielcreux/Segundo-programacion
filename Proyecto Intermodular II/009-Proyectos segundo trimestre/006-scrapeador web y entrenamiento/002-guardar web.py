import requests
import os

url = "https://tameformacion.com/"
output_folder = "paginas_html"
output_file = "example.html"

# Create folder if it does not exist
os.makedirs(output_folder, exist_ok=True)

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    html_content = response.text

    # Full path for the saved file
    filepath = os.path.join(output_folder, output_file)

    # Save HTML to disk
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML saved to: {filepath}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

