from fastapi import APIRouter
from models.intent_model import UserRequest, UserResponse
from utils.openai_client import detect_intent, call_openai
from pipelines import (
    document_analysis,
    policy_search,
    employee_data_access,
    document_generation,
    admin_function
)

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
    else:
        # Fallback chatbot classique (intent "Other" ou inconnu)
        try:
            reply = await call_openai(request.prompt)
            result = {
                "intent": "Other",
                "response": reply
            }
        except Exception as e:
            result = {
                "intent": "Other",
                "response": f"Erreur OpenAI: {e}"
            }

    if not isinstance(result, dict) or "intent" not in result or "response" not in result:
        return UserResponse(intent="Unknown", response="Invalid response structure from pipeline.")

    return UserResponse(**result)
