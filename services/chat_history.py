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
    if conversation_id is None:
        conversation_id = f"{username}_{datetime.utcnow().isoformat()}"

    item = {
        "id": conversation_id,
        "username": username,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": messages,
    }

    if title:
        item["title"] = title

    container.upsert_item(item)
    return conversation_id

def load_conversations(username):
    query = "SELECT * FROM c WHERE c.username = @username ORDER BY c.timestamp DESC"
    parameters = [{"name": "@username", "value": username}]
    return list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

def delete_conversation(conversation_id):
    container.delete_item(item=conversation_id, partition_key=conversation_id.split("_")[0])

def update_conversation_title_if_empty(username, prompt):
    conversations = load_conversations(username)
    if not conversations:
        return

    latest = conversations[0]
    if "title" not in latest or not latest["title"].strip():
        try:
            from services.rag_engine import call_openai
            title_prompt = f"Crée un court titre descriptif pour cette conversation : {prompt}"
            title = call_openai(title_prompt)
            latest["title"] = title.strip().strip('"')
            container.upsert_item(latest)
        except Exception:
            pass
