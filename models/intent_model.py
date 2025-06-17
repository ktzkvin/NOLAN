from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    prompt: str = Field(..., example="Quelle est la durée annuelle de travail pour un cadre en forfait jours ?")

class UserResponse(BaseModel):
    intent: str
    response: str