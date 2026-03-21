"""
Схемы для создания и управления психологами (только для админа).
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class PsychologistCreate(BaseModel):
    """Схема для создания психолога администратором."""
    
    full_name: str = Field(
        min_length=3,
        max_length=255,
        description="ФИО психолога"
    )
    email: EmailStr = Field(
        description="Email психолога"
    )
    phone: str = Field(
        min_length=10,
        max_length=20,
        description="Телефон психолога"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Пароль от 8 до 100 символов"
    )
    access_until: Optional[datetime] = Field(
        default=None,
        description="Дата и время окончания доступа (опционально)"
    )
    send_email: bool = Field(
        default=True,
        description="Отправить данные на email психолога"
    )


class PsychologistUpdate(BaseModel):
    full_name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=255,
        description="ФИО психолога"
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=20,
        description="Телефон психолога"
    )
    access_until: Optional[datetime] = Field(
        default=None,
        description="Дата и время окончания доступа"
    )
    is_blocked: Optional[bool] = Field(
        default=None,
        description="Заблокирован ли психолог"
    )


class PsychologistResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: str
    access_until: Optional[str] = None
    is_blocked: bool
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True



class PsychologistProfileUpdate(BaseModel):
    about_markdown: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Описание психолога в формате Markdown"
    )
