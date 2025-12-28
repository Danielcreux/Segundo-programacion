#!/usr/bin/env python3
import requests
import json
import urllib3

# Disable SSL warnings (because we're using verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://covalently-untasked-daphne.ngrok-free.dev/api.php"
API_KEY = "TEST_API_KEY_JOCARSA_123"   # Change to your real key


def main():
    question = input("Pregunta: ").strip()

    if not question:
        print("No se ha introducido ninguna pregunta.")
        return

    try:
        response = requests.post(
            API_URL,
            headers={"X-API-Key": API_KEY},
            data={"question": question},
            timeout=120,
            verify=False  # ngrok certificate is not verified
        )
    except Exception as e:
        print("Error al conectar con la API:", e)
        return

    if response.status_code != 200:
        print(f"Error del servidor (HTTP {response.status_code})")
        return

    try:
        payload = response.json()
    except json.JSONDecodeError:
        print("Respuesta no válida del servidor:")
        print(response.text)
        return

    answer = payload.get("answer")
    if answer is None:
        print("La respuesta no contiene el campo 'answer'.")
        return

    print(answer)


if __name__ == "__main__":
    main()
