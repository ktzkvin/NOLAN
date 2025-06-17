from utils.embedding import chunk_text, truncate_text, safe_embed
from utils.similarity import retrieve_relevant_chunks
from services.file_loader import load_all_files_from_blob
import os

chunk_vectors = []

def initialize_embeddings():
    texts = load_all_files_from_blob()
    for text in texts:
        for chunk in chunk_text(text):
            short_chunk = truncate_text(chunk)
            vec = safe_embed(short_chunk)["data"][0]["embedding"]
            chunk_vectors.append((chunk, vec))

def build_prompt(chunks, question):
    context = "\n\n".join(chunks)
    return f"""
Tu es un assistant professionnel. Réponds strictement à la question en utilisant uniquement les données fournies.

NE PAS INVENTER. Ne pas générer d'informations personnelles. Aucun contenu sensible.

CONNAISSANCES :
{context}

QUESTION :
{question}

RÉPONSE :
"""

def ask_rag(question):
    top_chunks = retrieve_relevant_chunks(question, chunk_vectors)
    prompt = build_prompt(top_chunks, question)
    import openai
    DEPLOYMENT_NAME = os.getenv("AZURE_MODEL_DEPLOYMENT")
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0]["message"]["content"].strip()