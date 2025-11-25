import subprocess
import json

# Ask for the prompt dynamically (or replace this with a variable)
prompt = input("Introduce el prompt: ")

# Build the payload
payload = {
    "model": "qwen3-coder:480b-cloud",
    "prompt": prompt
}

# Execute the curl command
result = subprocess.run(
    [
        "curl", "-s", "http://localhost:11434/api/generate",
        "-d", json.dumps(payload)
    ],
    capture_output=True,
    text=True
)

# Filter and print response like your jq + tr pipeline
try:
    lines = result.stdout.splitlines()
    response = ""
    for line in lines:
        obj = json.loads(line)
        if "response" in obj and obj["response"] is not None:
            response += obj["response"]
    print(response.strip())
except Exception as e:
    print("Error parsing output:", e)
    print(result.stdout)

