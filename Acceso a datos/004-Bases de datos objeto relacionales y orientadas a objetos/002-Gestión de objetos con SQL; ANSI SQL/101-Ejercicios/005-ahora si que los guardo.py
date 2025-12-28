# dependencias:
# pip install chromadb requests
# ollama pull nomic-embed-text

import requests
import chromadb
# from chromadb.config import Settings  # <- ELIMINAR

# ---------- 1. Función para obtener embeddings desde Ollama ----------

def ollama_embed(texts, model_name: str = "nomic-embed-text"):
    """
    Recibe una lista de textos y devuelve una lista de vectores (embeddings)
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


# ---------- 2. Inicializar cliente de Chroma (persistente, NUEVO) ----------

client = chromadb.PersistentClient(path="./chroma_ollama_frases")

collection = client.get_or_create_collection(
    name="frases_motivacionales",
    # aquí de momento no necesitamos embedding_function, porque tú le pasas los
    # embeddings explícitamente al hacer add()
    metadata={"hnsw:space": "cosine"}  # opcional, puedes incluso quitarlo
)


# ---------- 3. Definir las frases y autores (las de tu INSERT SQL) ----------

frases = [
    {
        "texto": "La vida es aquello que te ocurre mientras estás ocupado haciendo otros planes.",
        "autor": "John Lennon",
    },
    {
        "texto": "El éxito es la suma de pequeños esfuerzos repetidos día tras día.",
        "autor": "Robert Collier",
    },
    {
        "texto": "No cuentes los días, haz que los días cuenten.",
        "autor": "Muhammad Ali",
    },
    {
        "texto": "La simplicidad es la máxima sofisticación.",
        "autor": "Leonardo da Vinci",
    },
    {
        "texto": "El conocimiento es poder.",
        "autor": "Francis Bacon",
    },
    {
        "texto": "Si buscas resultados distintos, no hagas siempre lo mismo.",
        "autor": "Albert Einstein",
    },
    {
        "texto": "La imaginación lo es todo. Es la vista previa de las próximas atracciones de la vida.",
        "autor": "Albert Einstein",
    },
    {
        "texto": "No dejes para mañana lo que puedas hacer hoy.",
        "autor": "Benjamin Franklin",
    },
    {
        "texto": "Nunca es tarde para ser lo que podrías haber sido.",
        "autor": "George Eliot",
    },
    {
        "texto": "El futuro pertenece a quienes creen en la belleza de sus sueños.",
        "autor": "Eleanor Roosevelt",
    },
]

textos = [f["texto"] for f in frases]
autores = [f["autor"] for f in frases]
ids = [f"frase_{i+1}" for i in range(len(frases))]


# ---------- 4. Generar embeddings con Ollama ----------

print("Generando embeddings con Ollama...")
embeddings = ollama_embed(textos)  # list[list[float]]
print(f"Generados {len(embeddings)} embeddings.")
print(embeddings)

# ---------- 5. Guardar en Chroma ----------

collection.add(
    ids=ids,
    documents=textos,
    metadatas=[{"autor": autor} for autor in autores],
    embeddings=embeddings,
)

print("✅ Frases insertadas en Chroma y base persistida en ./chroma_ollama_frases")

