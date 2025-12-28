#!/usr/bin/env python3
import requests
import json

API_URL = "https://covalently-untasked-daphne.ngrok-free.dev/api.php"
API_KEY = "TEST_API_KEY_JOCARSA_123"   # Change to your real API key


def main():
    print("Jocarsa AI Client")
    print("------------------")
    question = input("Enter your question: ").strip()

    if not question:
        print("No question entered.")
        return

    try:
        response = requests.post(
            API_URL,
            headers={"X-API-Key": API_KEY},
            data={"question": question},
            timeout=120,
            verify=False  # your ngrok SSL is self-signed
        )
    except Exception as e:
        print("Error contacting API:", e)
        return

    if response.status_code != 200:
        print(f"Server returned HTTP {response.status_code}")
        print(response.text)
        return

    try:
        payload = response.json()
    except json.JSONDecodeError:
        print("Invalid JSON received:")
        print(response.text)
        return

    answer = payload.get("answer")
    if answer is None:
        print("No 'answer' field in the response.")
        print(payload)
        return

    print("\n--- ANSWER ---")
    print(answer)
    print("--------------\n")


if __name__ == "__main__":
    main()
