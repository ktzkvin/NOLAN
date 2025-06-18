from fastapi import APIRouter
from models.intent_model import UserRequest, UserResponse
from utils.openai_client import detect_intent
from pipelines import (
    document_analysis,
    policy_search,
    employee_data_access,
    document_generation,
    admin_function
)
from services.rag_engine import call_openai, ask_rag

router = APIRouter()

@router.post("/")
async def orchestrate(request: UserRequest):
    intent = await detect_intent(request.prompt)

    if intent == "PolicySearch":
        result = await policy_search.handle(request.prompt)
    elif intent == "DocumentAnalysis":
        result = await document_analysis.handle(request.prompt)
    elif intent == "EmployeeDataAccess":
        result = await employee_data_access.handle(request.prompt)
    elif intent == "DocumentGeneration":
        result = await document_generation.handle(request.prompt)
    elif intent == "AdminFunction":
        result = await admin_function.handle(request.prompt)
    elif intent == "Autre":
        if not request.prompt or len(request.prompt.strip()) <= 2:
            result = {
                "intent": "Autre",
                "response": "Bonjour ! Comment puis-je vous aider ? 😊"
            }
        else:
            try:
                response_text = await call_openai(request.prompt)
                result = {
                    "intent": "Autre",
                    "response": response_text
                }
            except Exception as e:
                result = {
                    "intent": "Autre",
                    "response": f"Erreur lors de l'appel assistant : {e}"
                }
    else:
        result = {
            "intent": "Unknown",
            "response": "Je n'ai pas pu comprendre la demande."
        }

    if not isinstance(result, dict):
        result = {
            "intent": "Erreur",
            "response": str(result)
        }

    return UserResponse(**result)
