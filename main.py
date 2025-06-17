from fastapi import FastAPI
from orchestrator import router

app = FastAPI(title="NOLAN Orchestrator")
app.include_router(router.router, prefix="/orchestrate")