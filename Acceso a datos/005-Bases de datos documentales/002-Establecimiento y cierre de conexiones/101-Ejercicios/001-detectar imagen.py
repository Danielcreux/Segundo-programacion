import base64, requests

with open("gato.jpg","rb") as f:
    img = base64.b64encode(f.read()).decode()

r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model":"llava",
        "prompt":"what is in this image?",
        "images":[img],
        "stream": False
    }
)

print(r.json()["response"])

