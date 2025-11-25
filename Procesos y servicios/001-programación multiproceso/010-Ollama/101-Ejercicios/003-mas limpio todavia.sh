curl -s http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct-q4_0",
  "prompt": "Resume qué es el aprendizaje automático en una sola frase."
}' | jq -r 'select(.response != null) | .response' | tr -d '\n'; echo

sudo snap restart ollama
