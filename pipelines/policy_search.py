from services.rag_engine import ask_rag

async def handle(prompt: str) -> str:
    return ask_rag(prompt)