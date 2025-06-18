import os
import openai
from utils.embedding import chunk_text, truncate_text, safe_embed
from utils.similarity import retrieve_relevant_chunks
from services.file_loader import load_all_files_from_blob
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("AZURE_MODEL_DEPLOYMENT")

# Pré‐charge une seule fois tous les embeddings
chunk_vectors = []
def initialize_embeddings():
    if chunk_vectors:
        return
    texts = load_all_files_from_blob()
    for text in texts:
        for chunk in chunk_text(text):
            vec = safe_embed(truncate_text(chunk))["data"][0]["embedding"]
            chunk_vectors.append((chunk, vec))

def build_prompt(chunks, question):
    context = "\n\n".join(chunks)
    return f"""
Tu es un assistant RH professionnel. Réponds strictement à la question
en utilisant uniquement les informations fournies ci-dessous (RAG).
Ne rajoute ni salutations, ni formules de politesse, ni balises markdown.

CONNAISSANCES :
{context}

QUESTION :
{question}

RÉPONSE :
"""

def ask_rag(question: str) -> str:
    initialize_embeddings()
    top_chunks = retrieve_relevant_chunks(question, chunk_vectors)
    prompt = build_prompt(top_chunks, question)
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

# Fallback : assistant généraliste (pour toute autre demande)
async def call_openai(prompt: str) -> str:
    """
    Ce fallback est utilisé pour toutes les intentions 'Autre' ou 'Fallback'.
    On laisse une petite formule de politesse ici.
    """
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant RH professionnel et courtois. "
                    "Réponds calmement et poliment à la question."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()
