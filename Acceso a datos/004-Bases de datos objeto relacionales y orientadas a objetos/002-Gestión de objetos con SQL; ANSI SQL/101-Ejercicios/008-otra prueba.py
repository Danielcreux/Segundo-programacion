# dependencias:
# pip install chromadb requests
# ollama pull nomic-embed-text

import requests
import chromadb

# ---------- 1. Función para obtener embeddings desde Ollama ----------

def ollama_embed(texts, model_name: str = "nomic-embed-text"):
    """
    Recibe un string o una lista de strings y devuelve una lista de vectores (embeddings)
    usando la API de Ollama en localhost:11434.
    """
    if isinstance(texts, str):
        texts = [texts]

    embeddings = []
    for text in texts:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": model_name,
                "prompt": text
            }
        )
        response.raise_for_status()
        data = response.json()
        embeddings.append(data["embedding"])
    return embeddings


# ---------- 2. Conectar con la base de Chroma existente ----------

client = chromadb.PersistentClient(path="./chroma_ollama_frases")
collection = client.get_collection("frases_motivacionales")


# ---------- 3. Frase nueva para buscar similitudes ----------

nueva_frase = "haz hoy lo que puedas, y no lo dejes para mañana"

if not nueva_frase:
    print("No se ha introducido ninguna frase.")
    exit(0)

# Obtener embedding de la frase de consulta
embedding_consulta = ollama_embed(nueva_frase)[0]


# ---------- 4. Consultar Chroma por similitud (solo mejor resultado) ----------

resultados = collection.query(
    query_embeddings=[embedding_consulta],
    n_results=1,  # <-- solo queremos la mejor coincidencia
    include=["documents", "metadatas"],  # no necesitamos distances ni embeddings
)


# ---------- 5. Mostrar SOLO la mejor coincidencia (best guess) ----------

print("\nFrase de consulta:")
print(f"  {nueva_frase}\n")

docs = resultados["documents"][0]
metas = resultados["metadatas"][0]
ids = resultados["ids"][0]

# como n_results=1, solo hay un elemento
mejor_doc = docs[0]
mejor_meta = metas[0]
mejor_id = ids[0]

print("Mejor coincidencia encontrada:")
print(f"ID:     {mejor_id}")
print(f"Autor:  {mejor_meta.get('autor', 'Desconocido')}")
print(f"Frase:  {mejor_doc}")

