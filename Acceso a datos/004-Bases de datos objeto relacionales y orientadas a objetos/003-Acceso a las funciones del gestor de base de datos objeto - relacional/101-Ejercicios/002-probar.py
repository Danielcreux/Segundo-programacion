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


# ---------- 2. Conectar con Chroma (corpus ya indexado) ----------

client = chromadb.PersistentClient(path="./chroma_ollama_corpus")
collection = client.get_collection("corpus_clases_md")


# ---------- 3. Bucle de consultas ----------

print("Buscador sobre tus clases (enter vacío para salir)\n")

while True:
    consulta = input("Escribe tu pregunta o tema: ").strip()
    if not consulta:
        print("Saliendo.")
        break

    # Obtener embedding de la consulta
    try:
        embedding_consulta = ollama_embed(consulta)[0]
    except Exception as e:
        print(f"Error obteniendo embedding desde Ollama: {e}")
        continue

    # Consultar Chroma por similitud (mejor resultado)
    try:
        resultados = collection.query(
            query_embeddings=[embedding_consulta],
            n_results=1,
            include=["documents", "metadatas"],  # ids vienen siempre
        )
    except Exception as e:
        print(f"Error consultando Chroma: {e}")
        continue

    if not resultados["documents"] or not resultados["documents"][0]:
        print("No se han encontrado fragmentos relevantes.")
        continue

    best_doc = resultados["documents"][0][0]
    best_meta = resultados["metadatas"][0][0]
    best_id = resultados["ids"][0][0]

    archivo = best_meta.get("archivo", "desconocido")
    indice = best_meta.get("indice_fragmento", "N/A")

    print("\n=== MEJOR COINCIDENCIA EN EL CORPUS ===")
    print(f"ID:        {best_id}")
    print(f"Archivo:   {archivo}")
    print(f"Fragmento: #{indice}")
    print("----------------------------------------")
    print(best_doc)
    print("========================================\n")

