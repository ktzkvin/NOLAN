from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    prompt: str = Field(..., example="Donne toutes les infos de John Smith dans la base RH")

class UserResponse(BaseModel):
    intent: str
    response: str