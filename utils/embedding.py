import tiktoken
import openai
import os
import time
from openai.error import RateLimitError

enc = tiktoken.get_encoding("cl100k_base")
MAX_EMBED_TOKENS = 8192
EMBEDDING_NAME = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

def chunk_text(text, max_tokens=500):
    paragraphs = text.split("\n\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(enc.encode(current + para)) > max_tokens:
            chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para
    chunks.append(current.strip())
    return chunks

def truncate_text(text, max_tokens=MAX_EMBED_TOKENS):
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens]) if len(tokens) > max_tokens else text

def safe_embed(text):
    for _ in range(3):
        try:
            return openai.Embedding.create(input=text, engine=EMBEDDING_NAME)
        except RateLimitError:
            time.sleep(60)
    raise RuntimeError("Embedding failed after 3 retries")