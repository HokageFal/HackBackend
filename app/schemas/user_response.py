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
    full_name: str
    email: str
    phone: str
    photo_url: Optional[str] = None
    about_markdown: Optional[str] = None
    role: str
    is_admin: bool
    access_until: Optional[datetime] = None
    is_blocked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
