from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500, description="Название теста")
    access_until: Optional[datetime] = Field(default=None, description="Дата и время окончания доступа")
    client_can_view_report: bool = Field(default=False, description="Может ли клиент видеть отчет")


class ProfileFieldUpdate(BaseModel):
    id: Optional[int] = Field(default=None, description="ID поля (если обновление существующего)")
    label: str = Field(min_length=1, max_length=200, description="Название поля")
    field_type: str = Field(description="Тип поля: text, number, date, datetime")
    is_required: bool = Field(default=True, description="Обязательное ли поле")
    position: int = Field(ge=0, description="Порядок отображения")


class SectionUpdate(BaseModel):
    id: Optional[int] = Field(default=None, description="ID секции (если обновление существующей)")
    title: str = Field(min_length=1, max_length=500, description="Название секции")
    display_order: int = Field(ge=0, description="Порядок отображения")


class QuestionOptionUpdate(BaseModel):
    id: Optional[int] = Field(default=None, description="ID опции (если обновление существующей)")
    option_text: str = Field(min_length=1, max_length=1000, description="Текст опции")
    option_value: Optional[float] = Field(default=None, description="Числовое значение опции")
    display_order: int = Field(ge=0, description="Порядок отображения")


class QuestionUpdate(BaseModel):
    id: Optional[int] = Field(default=None, description="ID вопроса (если обновление существующего)")
    section_id: Optional[int] = Field(default=None, description="ID секции")
    question_text: str = Field(min_length=1, max_length=2000, description="Текст вопроса")
    question_type: str = Field(description="Тип вопроса: single_choice, multiple_choice, text, number, boolean, datetime")
    is_required: bool = Field(default=True, description="Обязательный ли вопрос")
    display_order: int = Field(ge=0, description="Порядок отображения")
    settings: Optional[dict] = Field(default=None, description="Дополнительные настройки вопроса")
    options: Optional[list[QuestionOptionUpdate]] = Field(default=None, description="Опции для вопроса")


class MetricUpdate(BaseModel):
    id: Optional[int] = Field(default=None, description="ID метрики (если обновление существующей)")
    metric_name: str = Field(min_length=1, max_length=200, description="Название метрики")
    formula: str = Field(min_length=1, description="Формула расчета метрики")
    description: Optional[str] = Field(default=None, max_length=1000, description="Описание метрики")


class ReportTemplateUpdate(BaseModel):
    id: Optional[int] = Field(default=None, description="ID шаблона (если обновление существующего)")
    audience: str = Field(description="Аудитория: client или psychologist")
    template_definition: dict = Field(description="Определение шаблона отчета")


class TestUpdate(BaseModel):
    """Обновление теста со всеми вложенными данными"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Название теста")
    access_until: Optional[datetime] = Field(default=None, description="Дата и время окончания доступа")
    client_can_view_report: Optional[bool] = Field(default=None, description="Может ли клиент видеть отчет")
    profile_fields: Optional[list[ProfileFieldUpdate]] = Field(default=None, description="Поля профиля")
    sections: Optional[list[SectionUpdate]] = Field(default=None, description="Секции теста")
    questions: Optional[list[QuestionUpdate]] = Field(default=None, description="Вопросы теста")
    metrics: Optional[list[MetricUpdate]] = Field(default=None, description="Метрики теста")
    report_templates: Optional[list[ReportTemplateUpdate]] = Field(default=None, description="Шаблоны отчетов")


class TestResponse(BaseModel):
    id: int
    psychologist_id: int
    title: str
    public_link_token: str
    access_until: Optional[str] = None
    client_can_view_report: bool
    attempts_count: int
    
    class Config:
        from_attributes = True


class TestLinkResponse(BaseModel):
    test_id: int
    title: str
    public_link: str
    public_link_token: str


class TestExportData(BaseModel):
    test: dict
    profile_fields: list[dict]
    sections: list[dict]
    questions: list[dict]
    question_options: list[dict]
    metrics: list[dict]
    report_templates: list[dict]
