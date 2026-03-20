"""
Схемы для создания и управления психологами (только для админа).
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date
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
    access_until: Optional[date] = Field(
        default=None,
        description="Дата окончания доступа (опционально)"
    )
    send_email: bool = Field(
        default=True,
        description="Отправить данные на email психолога"
    )


class PsychologistUpdate(BaseModel):
    """Схема для обновления доступа психолога."""
    
    access_until: Optional[date] = Field(
        default=None,
        description="Дата окончания доступа"
    )
    is_blocked: Optional[bool] = Field(
        default=None,
        description="Заблокирован ли психолог"
    )
