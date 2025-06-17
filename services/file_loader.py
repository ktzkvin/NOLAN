import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from pathlib import Path
import pandas as pd
from docx import Document
import fitz

BLOB_CONTAINER = "nolan-rag-files"
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def load_all_files_from_blob() -> list[str]:
    docs = []
    for blob in container_client.list_blobs():
        try:
            downloader = container_client.download_blob(blob.name)
            data = BytesIO(downloader.readall())
            ext = Path(blob.name).suffix.lower()

            if ext == ".txt":
                content = data.read().decode("utf-8", errors="ignore")
            elif ext == ".pdf":
                doc = fitz.open(stream=data, filetype="pdf")
                content = "\n".join(page.get_text() for page in doc)
            elif ext == ".docx":
                doc = Document(data)
                content = "\n".join(p.text for p in doc.paragraphs)
            elif ext == ".csv":
                try:
                    df = pd.read_csv(data, encoding="utf-8")
                except UnicodeDecodeError:
                    data.seek(0)
                    df = pd.read_csv(data, encoding="latin1")
                content = df.to_string(index=False)
            else:
                continue

            if content.strip():
                docs.append(content)
        except:
            continue
    return docs

# 🔽 Ajoute ceci
def load_blob_file(filename: str) -> bytes:
    blob_client = container_client.get_blob_client(blob=filename)
    data = blob_client.download_blob().readall()
    return data