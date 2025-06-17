import numpy as np
import openai
import os

EMBEDDING_NAME = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

def cosine_sim(v1, v2):
    a, b = np.array(v1), np.array(v2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_relevant_chunks(question, chunk_vectors, top_k=3):
    q_vec = openai.Embedding.create(input=question, engine=EMBEDDING_NAME)["data"][0]["embedding"]
    ranked = sorted(chunk_vectors, key=lambda x: cosine_sim(x[1], q_vec), reverse=True)
    return [c[0] for c in ranked[:top_k]]