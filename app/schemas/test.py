from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500, description="Название теста")
    access_until: Optional[datetime] = Field(default=None, description="Дата и время окончания доступа")
    client_can_view_report: bool = Field(default=False, description="Может ли клиент видеть отчет")


class TestUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500, description="Название теста")
    access_until: Optional[datetime] = Field(default=None, description="Дата и время окончания доступа")
    client_can_view_report: Optional[bool] = Field(default=None, description="Может ли клиент видеть отчет")


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
