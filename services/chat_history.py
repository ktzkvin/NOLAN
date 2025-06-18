import os
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")

if not COSMOS_URL or not COSMOS_KEY:
    raise ValueError("COSMOS_URL ou COSMOS_KEY non défini ou vide")

client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
db = client.get_database_client("nolan")
container = db.get_container_client("chat_history")

def save_conversation(convo_id, username, messages):
    container.upsert_item({
        "id": convo_id,
        "username": username,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages
    })

def load_conversations(username):
    query = "SELECT * FROM c WHERE c.username = @username ORDER BY c.timestamp DESC"
    parameters = [{"name": "@username", "value": username}]
    return list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

def delete_conversation(convo_id, username):
    container.delete_item(item=convo_id, partition_key=username)
