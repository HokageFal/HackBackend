from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreatedResponse(BaseModel):
    message: str
    user_id: int

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    message: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    is_admin: bool
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
