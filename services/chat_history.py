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

def save_conversation(username, messages, conversation_id=None, title=None):
    # si on ré-ouvre une conversation existante, on récupère son ancien titre
    if conversation_id:
        try:
            existing = container.read_item(item=conversation_id, partition_key=username)
            old_title = existing.get("title")
        except:
            old_title = None
    else:
        # nouvelle conversation
        conversation_id = f"{username}_{datetime.utcnow().isoformat()}"
        old_title = None

    item = {
        "id": conversation_id,
        "username": username,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages,
    }

    # si on a un titre tout frais ou conservé, on l’ajoute
    final_title = title or old_title
    if final_title:
        item["title"] = final_title

    container.upsert_item(item)
    return conversation_id

def load_conversations(username):
    query = "SELECT * FROM c WHERE c.username = @username ORDER BY c.timestamp DESC"
    parameters = [{"name": "@username", "value": username}]
    return list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

def delete_conversation(conversation_id):
    username = conversation_id.split("_")[0]
    container.delete_item(item=conversation_id, partition_key=username)
