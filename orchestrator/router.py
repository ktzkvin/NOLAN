from fastapi import APIRouter
from models.intent_model import UserRequest, UserResponse
from utils.openai_client import detect_intent
from pipelines import (
    document_analysis, 
    # to be implemented
)

router = APIRouter()

@router.post("/")
async def orchestrate(request: UserRequest):
    intent = await detect_intent(request.prompt)
    
    if intent == "DocumentAnalysis":
        result = await document_analysis.handle(request.prompt)
    elif intent == "PolicySearch":
        result = 'await policy_search.handle(request.prompt)'
    elif intent == "EmployeeDataAccess":
        result = 'await employee_data.handle(request.prompt)'
    elif intent == "DocumentGeneration":
        result = 'await document_generation.handle(request.prompt)'
    elif intent == "AdminFunction":
        result = 'await admin.handle(request.prompt)'
    else:
        result = "I'm sorry, I don't understand. Could you please rephrase?"
    
    return UserResponse(intent=intent, response=result)
