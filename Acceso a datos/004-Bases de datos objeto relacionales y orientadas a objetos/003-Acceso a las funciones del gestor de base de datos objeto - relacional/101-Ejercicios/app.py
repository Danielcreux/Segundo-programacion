import os
import requests
from flask import Flask, render_template, request, jsonify
import chromadb

# ----------------- Configuration ----------------- #

OLLAMA_BASE_URL = "http://localhost:11434"
CHAT_MODEL = "qwen2.5:3b-instruct"          # change if you use another chat model
EMBED_MODEL = "nomic-embed-text" # embedding model

CHROMA_PATH = "./chroma_ollama_corpus"
CHROMA_COLLECTION = "corpus_clases_md"

# ----------------- Flask app ----------------- #

app = Flask(__name__)

# ----------------- Chroma connection ----------------- #

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(CHROMA_COLLECTION)


# ----------------- Embeddings via Ollama ----------------- #

def ollama_embed(texts, model_name: str = EMBED_MODEL):
    """
    Takes a string or a list of strings and returns a list of embeddings.
    """
    if isinstance(texts, str):
        texts = [texts]

    embeddings = []
    for text in texts:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": model_name,
                "prompt": text
            }
        )
        response.raise_for_status()
        data = response.json()
        embeddings.append(data["embedding"])
    return embeddings


# ----------------- Retrieval from Chroma ----------------- #

def retrieve_context(query: str, top_k: int = 5):
    """
    Given a user query, returns the top_k most similar fragments from the corpus.
    """
    query_embedding = ollama_embed(query)[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # Build a text block with the retrieved context
    context_blocks = []
    for doc, meta in zip(docs, metas):
        archivo = meta.get("archivo", "desconocido")
        indice = meta.get("indice_fragmento", "N/A")
        context_blocks.append(
            f"[Archivo: {archivo} | Fragmento: {indice}]\n{doc}"
        )

    full_context = "\n\n---\n\n".join(context_blocks)
    return full_context, context_blocks


# ----------------- Generation via Ollama (RAG) ----------------- #

def generate_answer(user_query: str, context: str) -> str:
    """
    Calls Ollama /api/chat with the retrieved context and user query.
    """
    system_prompt = (
        "Eres un profesor que responde usando únicamente la información "
        "proveniente del contexto de transcripciones de clases. "
        "Si el contexto no contiene la respuesta, dilo explícitamente.\n\n"
        "Responde en español, de forma clara y breve."
    )

    user_message = (
        "Contexto de referencia (transcripciones):\n"
        f"{context}\n\n"
        "Pregunta del usuario:\n"
        f"{user_query}\n\n"
        "Respuesta:"
    )

    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload
    )
    response.raise_for_status()
    data = response.json()

    # Ollama /api/chat returns {"message": {"content": "..."} , ...}
    answer = data["message"]["content"]
    return answer


# ----------------- Routes ----------------- #

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        context, context_blocks = retrieve_context(user_message, top_k=5)
        answer = generate_answer(user_message, context)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "answer": answer,
        "context_snippets": context_blocks,  # optional, for debugging or UI
    })


if __name__ == "__main__":
    # For development only; in production use gunicorn/uwsgi + reverse proxy
    app.run(host="0.0.0.0", port=5000, debug=True)

