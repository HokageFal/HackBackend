from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.response_utils import (
    create_success_response,
    create_server_error,
    create_not_found_error,
    create_forbidden_error
)
from app.core.dependencies import get_current_psychologist, AccessDeniedError
from app.schemas.api_response import SuccessResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/attempts", tags=["Attempts"])


@router.get(
    "/{attempt_id}",
    response_model=SuccessResponse,
    summary="Получить детальную информацию о прохождении",
    description="""
    Возвращает полную информацию о конкретном прохождении теста.
    
    **Доступ:**
    - Только психолог-владелец теста
    
    **Возвращает:**
    - Данные профиля клиента
    - Все ответы на вопросы
    - Выбранные опции для choice вопросов
    - Статус прохождения
    
    **Использование:**
    - Детальный просмотр результатов клиента
    - Перед генерацией отчета
    - Для анализа ответов
    """,
    responses={
        200: {
            "description": "Детали прохождения получены",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Детали прохождения получены",
                        "data": {
                            "attempt_id": 123,
                            "test_id": 1,
                            "test_title": "Тест на профориентацию",
                            "client_name": "Иванов Иван Иванович",
                            "started_at": "2026-03-21T10:00:00",
                            "submitted_at": "2026-03-21T10:45:00",
                            "status": "completed",
                            "profile_data": [
                                {
                                    "field_id": 1,
                                    "field_name": "Возраст",
                                    "field_type": "number",
                                    "value": "25"
                                }
                            ],
                            "answers": [
                                {
                                    "question_id": 1,
                                    "question_text": "Как вас зовут?",
                                    "question_type": "text",
                                    "answer_value": "Иван",
                                    "selected_options": None
                                },
                                {
                                    "question_id": 2,
                                    "question_text": "Выберите цвет",
                                    "question_type": "single_choice",
                                    "answer_value": None,
                                    "selected_options": [
                                        {
                                            "option_id": 5,
                                            "option_text": "Синий",
                                            "option_value": 2
                                        }
                                    ]
                                }
                            ]
                        },
                        "errors": None
                    }
                }
            }
        },
        403: {
            "description": "Нет доступа к результатам"
        },
        404: {
            "description": "Попытка не найдена"
        }
    }
)
async def get_attempt_details_endpoint(
    attempt_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    from app.services.attempt_results_service import (
        get_attempt_details_service,
        AttemptNotFound,
        AccessDenied
    )
    
    logger.info(
        "Get attempt details endpoint called",
        operation="get_attempt_details_endpoint",
        attempt_id=attempt_id
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        result = await get_attempt_details_service(
            session,
            attempt_id,
            psychologist.id
        )
        
        logger.info(
            "Attempt details retrieved successfully in endpoint",
            operation="get_attempt_details_endpoint",
            attempt_id=attempt_id
        )
        
        return create_success_response(
            message="Детали прохождения получены",
            data=result
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (AttemptNotFound, AccessDenied) as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(attempt_id),
            reason="Attempt not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get attempt details endpoint",
            operation="get_attempt_details_endpoint",
            attempt_id=attempt_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "/{attempt_id}/report/{audience}",
    summary="Сгенерировать отчет",
    description="""
    Генерирует отчет по результатам прохождения теста.
    
    **Доступ:**
    - Только психолог-владелец теста
    
    **Параметры:**
    - attempt_id: ID прохождения
    - audience: "client" или "psychologist"
    - format: "html" (по умолчанию) или "docx"
    
    **Форматы:**
    - HTML - для просмотра в браузере (возвращает JSON с content)
    - DOCX - для скачивания (возвращает файл напрямую)
    
    **Отчет включает:**
    - Данные профиля клиента
    - Все ответы на вопросы
    - Рассчитанные метрики
    - Графики (если настроены)
    
    **Важно:**
    - Отчет можно сформировать только для завершенных тестов
    - Разные шаблоны для клиента и психолога
    - Отчеты генерируются в реальном времени, не хранятся
    """,
    responses={
        200: {
            "description": "Отчет сгенерирован",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Отчет сгенерирован",
                        "data": {
                            "attempt_id": 123,
                            "test_title": "Тест на профориентацию",
                            "client_name": "Иванов Иван Иванович",
                            "audience": "client",
                            "format": "html",
                            "generated_at": "2026-03-21T14:00:00",
                            "content": "<!DOCTYPE html>..."
                        },
                        "errors": None
                    }
                }
            }
        },
        403: {
            "description": "Нет доступа или тест не завершен"
        },
        404: {
            "description": "Попытка или шаблон не найдены"
        }
    }
)
async def generate_report_endpoint(
    attempt_id: int,
    audience: str,
    format: str = "html",
    request: Request = None,
    session: AsyncSession = Depends(get_db)
):
    from app.services.attempt_results_service import (
        generate_report_service,
        AttemptNotFound,
        AccessDenied
    )
    from app.database.crud.test_attempt_crud import get_attempt_by_id
    
    logger.info(
        "Generate report endpoint called",
        operation="generate_report_endpoint",
        attempt_id=attempt_id,
        audience=audience,
        format=format
    )
    
    try:
        if audience not in ["client", "psychologist"]:
            raise create_not_found_error(
                field="audience",
                message="Аудитория должна быть 'client' или 'psychologist'",
                input_data=audience,
                reason="Invalid audience"
            )
        
        if format not in ["html", "docx"]:
            raise create_not_found_error(
                field="format",
                message="Формат должен быть 'html' или 'docx'",
                input_data=format,
                reason="Invalid format"
            )
        
        psychologist = await get_current_psychologist(request, session)
        
        result = await generate_report_service(
            session,
            attempt_id,
            psychologist.id,
            audience,
            format
        )
        
        logger.info(
            "Report generated successfully in endpoint",
            operation="generate_report_endpoint",
            attempt_id=attempt_id,
            audience=audience,
            format=format
        )
        
        if format == "docx":
            attempt = await get_attempt_by_id(session, attempt_id)
            filename = f"report_{audience}_{attempt.client_name}_{attempt_id}.docx"
            
            return StreamingResponse(
                result,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        
        return create_success_response(
            message="Отчет сгенерирован",
            data=result
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (AttemptNotFound, AccessDenied) as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(attempt_id),
            reason="Attempt not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in generate report endpoint",
            operation="generate_report_endpoint",
            attempt_id=attempt_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
