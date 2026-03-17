"""
User update schemas.
"""

from pydantic import BaseModel, Field, field_validator


class UserUpdateProfile(BaseModel):
    """Схема для обновления профиля пользователя."""
    
    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="Новое имя пользователя"
    )
    avatar_url: str | None = Field(
        None,
        max_length=500,
        description="Новый URL аватара"
    )
    
    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            raise ValueError("Имя пользователя не может быть пустым")
        return v
    
    @field_validator('avatar_url')
    @classmethod
    def avatar_url_not_empty(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            raise ValueError("URL аватара не может быть пустым")
        return v
