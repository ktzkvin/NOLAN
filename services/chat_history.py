import os
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")

# Debug si nécessaire
if not COSMOS_URL or not COSMOS_KEY:
    raise ValueError("COSMOS_URL ou COSMOS_KEY non défini ou vide")

# Connexion au client Cosmos DB
client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
db = client.get_database_client("nolan")
container = db.get_container_client("chat_history")

def save_conversation(username, messages):
    doc_id = f"{username}_{datetime.utcnow().isoformat()}"
    container.upsert_item({
        "id": doc_id,
        "username": username,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages
    })

def load_conversations(username):
    query = "SELECT * FROM c WHERE c.username = @username ORDER BY c.timestamp DESC"
    parameters = [{"name": "@username", "value": username}]
    return list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
