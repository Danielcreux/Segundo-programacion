import requests

url = "https://tameformacion.com/"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raises an error for 4xx/5xx responses

    html_content = response.text
    print(html_content)

except requests.exceptions.RequestException as e:
    print(f"Error obtaining the page: {e}")

