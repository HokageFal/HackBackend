from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class SubmissionAnswer(BaseModel):
    question_id: int = Field(..., description="ID вопроса")
    text_answer: Optional[str] = Field(None, description="Текстовый ответ")
    boolean_answer: Optional[bool] = Field(None, description="Да/Нет ответ")
    number_answer: Optional[Decimal] = Field(None, description="Числовой ответ")
    datetime_answer: Optional[datetime] = Field(None, description="Дата/время ответ")
    selected_option_ids: Optional[List[int]] = Field(None, description="ID выбранных опций")


class SubmissionProfileValue(BaseModel):
    profile_field_id: int = Field(..., description="ID поля профиля")
    text_value: Optional[str] = Field(None, description="Текстовое значение")
    number_value: Optional[Decimal] = Field(None, description="Числовое значение")
    date_value: Optional[str] = Field(None, description="Значение даты")
    datetime_value: Optional[datetime] = Field(None, description="Значение даты и времени")


class TestSubmission(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=255, description="ФИО клиента")
    profile_values: List[SubmissionProfileValue] = Field(default_factory=list, description="Данные профиля")
    answers: List[SubmissionAnswer] = Field(..., min_length=1, description="Ответы на вопросы")


class SubmissionResponse(BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    client_name: str
    submitted_at: datetime
    can_view_report: bool
    message: str
