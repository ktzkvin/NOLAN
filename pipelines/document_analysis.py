from services.rag_engine import ask_rag

async def handle(prompt: str) -> str:
    """
    DocumentAnalysis doit interroger le RAG sur le contenu des documents stockés
    pour extraire la réponse.
    """
    return ask_rag(prompt)