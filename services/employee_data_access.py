import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import BytesIO
import os

BLOB_NAME = "hr_dataset_fr_new.csv"
BLOB_CONTAINER = "nolan-rag-files"
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def load_hr_csv_from_blob() -> pd.DataFrame:
    blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container = blob_service.get_container_client(BLOB_CONTAINER)
    blob_data = container.download_blob(BLOB_NAME).readall()
    
    try:
        return pd.read_csv(BytesIO(blob_data), encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        return pd.read_csv(BytesIO(blob_data), encoding="latin1", on_bad_lines="skip")