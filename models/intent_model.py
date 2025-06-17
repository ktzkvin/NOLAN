from pydantic import BaseModel

class UserRequest(BaseModel):
    prompt: str

class UserResponse(BaseModel):
    intent: str
    response: str
