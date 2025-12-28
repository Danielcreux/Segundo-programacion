import requests
import json

sentence = "Esta es una frase de prueba"

response = requests.post(
    "http://localhost:11434/api/embeddings",
    json={
        "model": "nomic-embed-text",
        "prompt": sentence
    }
)

vector = response.json()["embedding"]

print("Embedding dimension:", len(vector))
print(vector)
print(vector[:10])