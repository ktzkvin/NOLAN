from fastapi import FastAPI
from orchestrator import router
from services.rag_engine import initialize_embeddings

initialize_embeddings()

app = FastAPI(title="NOLAN Orchestrator")
app.include_router(router.router, prefix="/orchestrate")