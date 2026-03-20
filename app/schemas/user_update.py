"""
User update schemas.
"""

from pydantic import BaseModel, Field, field_validator


class UserUpdateProfile(BaseModel):
    """Схема для обновления профиля психолога."""
    
    about_markdown: str | None = Field(
        None,
        description="Описание психолога в формате Markdown"
    )
    
    @field_validator('about_markdown')
    @classmethod
    def about_markdown_not_empty(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            raise ValueError("Описание не может быть пустым")
        return v
