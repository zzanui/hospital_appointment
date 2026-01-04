from pydantic import BaseModel, Field

class PatientLoginRequest(BaseModel):
    phone_number: str = Field(..., min_length=5)
    name: str | None = None

class PatientLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"