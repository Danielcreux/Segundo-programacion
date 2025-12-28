# dependencias:
# pip install chromadb requests
# ollama pull nomic-embed-text

import os
import glob
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


# ---------- 2. Función para trocear texto largo en fragmentos ----------

def chunk_text(text, max_chars=800):
    """
    Divide un texto en fragmentos de como máximo max_chars, procurando
    cortar por saltos de línea en lugar de a mitad de palabra.
    """
    fragments = []
    current = ""

    for line in text.splitlines(keepends=True):
        # Si añadir la línea supera el límite, cerramos fragmento
        if len(current) + len(line) > max_chars and current:
            fragments.append(current.strip())
            current = line
        else:
            current += line

    if current.strip():
        fragments.append(current.strip())

    # Filtrar fragmentos vacíos
    return [f for f in fragments if f.strip()]


# ---------- 3. Conectar con Chroma (base persistente para el corpus) ----------

client = chromadb.PersistentClient(path="./chroma_ollama_corpus")

collection = client.get_or_create_collection(
    name="corpus_clases_md",
    metadata={"descripcion": "Transcripciones de clases en Markdown"},
)


# ---------- 4. Recorrer todos los .md de la carpeta corpus/ ----------

base_path = "./corpus"
pattern = os.path.join(base_path, "**", "*.md")

files = glob.glob(pattern, recursive=True)

if not files:
    print("No se han encontrado archivos .md en la carpeta 'corpus/'.")
    exit(0)

print(f"Encontrados {len(files)} archivos .md en '{base_path}'.")


# ---------- 5. Indexar archivo a archivo ----------

global_counter = 0

for file_path in files:
    print(f"\nProcesando: {file_path}")

    # Leer contenido del archivo
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Trocear en fragmentos
    chunks = chunk_text(text, max_chars=800)

    if not chunks:
        print("  (Archivo vacío o sin texto útil, se omite)")
        continue

    print(f"  Fragmentos generados: {len(chunks)}")

    # Crear IDs y metadatos
    ids = []
    metadatas = []
    for idx, _ in enumerate(chunks):
        global_counter += 1
        chunk_id = f"chunk_{global_counter}"
        ids.append(chunk_id)

        metadatas.append({
            "archivo": os.path.relpath(file_path, base_path),
            "indice_fragmento": idx,
        })

    # ---------- NUEVO: manejo de errores de embeddings ----------
    try:
        embeddings = ollama_embed(chunks)
    except Exception as e:
        print(f"  ❌ ERROR al obtener embeddings:")
        print(f"     {str(e)}")
        print("  → Archivo saltado.\n")
        continue
    # ------------------------------------------------------------

    # Guardar en Chroma
    try:
        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings,
        )
    except Exception as e:
        print(f"  ❌ ERROR al insertar en Chroma:")
        print(f"     {str(e)}")
        print("  → Archivo saltado.\n")
        continue

    print(f"  Insertados {len(chunks)} fragmentos en la colección.")



print("\n✅ Indexación completada.")
print(f"Total de fragmentos insertados: {global_counter}")
print("Base vectorial en: ./chroma_ollama_corpus (colección: corpus_clases_md)")

