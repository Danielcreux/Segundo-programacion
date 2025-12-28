import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:9b-instruct-q4_0"

def ask_ollama(question: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": question,
        "stream": False   # set to True if you want streaming tokens
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "")

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    answer = ask_ollama(user_input)
    print("\n=== Ollama Response ===\n")
    print(answer)

