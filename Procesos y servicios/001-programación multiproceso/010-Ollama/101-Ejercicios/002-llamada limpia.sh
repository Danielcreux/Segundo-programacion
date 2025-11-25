curl -s http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct-q4_0",
  "prompt": "Dime una frase inspiradora sobre la programación."
}' | jq -r 'select(.response != null) | .response' | tr -d '\n'; echo

