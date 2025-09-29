from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama_helper import OllamaClient
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Ollama client
ollama = OllamaClient()

@app.route('/')
def home():
    return jsonify({"message": "Micro ChatGPT Backend is running!"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message']
        model = data.get('model', 'llama2')
        context = data.get('context')
        
        # Get response from Ollama
        result = ollama.chat(message, model, context)
        
        return jsonify({
            "response": result["response"],
            "context": result.get("context"),
            "success": result["success"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    try:
        models = ollama.get_available_models()
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if Ollama is running"""
    try:
        models = ollama.list_models()
        return jsonify({
            "status": "healthy",
            "ollama_connected": "error" not in models
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)