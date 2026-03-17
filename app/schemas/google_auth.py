from pydantic import BaseModel, Field


class GoogleAuthRequest(BaseModel):
    """Запрос с Google ID токеном от фронтенда"""
    token: str = Field(..., description="Google ID Token полученный на фронтенде")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI3..."
            }
        }
