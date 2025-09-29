# Create and activate virtual environment (optional but recommended)
py -m venv venv
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Make sure Ollama is running
ollama serve

# Start Flask server
python app.py