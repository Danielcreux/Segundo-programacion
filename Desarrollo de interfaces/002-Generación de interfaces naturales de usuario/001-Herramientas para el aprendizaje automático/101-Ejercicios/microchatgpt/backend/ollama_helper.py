import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def list_models(self):
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, message, model="llama2", context=None):
        """Send message to Ollama and get response"""
        try:
            payload = {
                "model": model,
                "prompt": message,
                "stream": False,
                "context": context
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result.get("response", ""),
                    "context": result.get("context"),
                    "success": True
                }
            else:
                return {
                    "response": f"Error: {response.status_code}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "response": f"Connection error: {str(e)}",
                "success": False
            }
    
    def get_available_models(self):
        """Get list of installed models"""
        models = self.list_models()
        if 'models' in models:
            return [model['name'] for model in models['models']]
        return []