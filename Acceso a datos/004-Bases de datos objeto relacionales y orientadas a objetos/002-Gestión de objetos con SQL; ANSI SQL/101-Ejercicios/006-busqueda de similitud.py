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

nueva_frase = "Aquello que te ocurre mientras haces otros planes, es la vida"

if not nueva_frase:
    print("No se ha introducido ninguna frase.")
    exit(0)

# Obtener embedding de la frase de consulta
embedding_consulta = ollama_embed(nueva_frase)[0]


# ---------- 4. Consultar Chroma por similitud ----------

n_resultados = 5  # cuántas frases quieres recuperar

resultados = collection.query(
    query_embeddings=[embedding_consulta],
    n_results=n_resultados,
    include=["documents", "metadatas", "distances"],  # <- sin "ids"
)

# ---------- 5. Mostrar resultados ----------

print("\nFrase de consulta:")
print(f"  {nueva_frase}")
print("\nFrases más similares:\n")

docs = resultados["documents"][0]
metas = resultados["metadatas"][0]
dists = resultados["distances"][0]
ids = resultados["ids"][0]  # se siguen devolviendo, aunque no vayan en include

for doc, meta, dist, _id in zip(docs, metas, dists, ids):
    print(f"ID:       {_id}")
    print(f"Autor:    {meta.get('autor', 'Desconocido')}")
    print(f"Distancia (menor = más similar): {dist:.4f}")
    print(f"Frase:    {doc}")
    print("-" * 60)

