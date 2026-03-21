from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class ProfileValueCreate(BaseModel):
    profile_field_id: int = Field(..., description="ID поля профиля")
    text_value: Optional[str] = Field(None, description="Текстовое значение")
    number_value: Optional[Decimal] = Field(None, description="Числовое значение")
    date_value: Optional[date] = Field(None, description="Значение даты")


class AttemptCreate(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=255, description="ФИО клиента (обязательно)")
    profile_values: List[ProfileValueCreate] = Field(default_factory=list, description="Значения полей профиля")


class AnswerCreate(BaseModel):
    question_id: int = Field(..., description="ID вопроса")
    text_answer: Optional[str] = Field(None, description="Текстовый ответ")
    boolean_answer: Optional[bool] = Field(None, description="Да/Нет ответ")
    number_answer: Optional[Decimal] = Field(None, description="Числовой ответ")
    datetime_answer: Optional[datetime] = Field(None, description="Дата/время ответ")
    selected_option_ids: Optional[List[int]] = Field(None, description="ID выбранных опций (для single/multiple choice)")

    @field_validator('selected_option_ids')
    @classmethod
    def validate_option_ids(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v


class AnswersSubmit(BaseModel):
    answers: List[AnswerCreate] = Field(..., min_length=1, description="Список ответов на вопросы")


class AttemptResponse(BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    client_name: str
    started_at: datetime
    total_questions: int


class ProgressResponse(BaseModel):
    attempt_id: int
    total_questions: int
    answered_questions: int
    progress_percent: float
    unanswered_question_ids: List[int]


class SubmitResponse(BaseModel):
    attempt_id: int
    submitted_at: datetime
    can_view_report: bool
    message: str
