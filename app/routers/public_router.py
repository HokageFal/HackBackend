from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.response_utils import (
    create_success_response,
    create_server_error,
    create_not_found_error
)
from app.schemas.api_response import SuccessResponse
from app.schemas.test_submission import TestSubmission
from app.services.test_service import (
    get_test_by_token_service,
    TestNotFound,
    TestAccessDenied
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/public", tags=["Public"])


@router.get(
    "/tests/{token}",
    response_model=SuccessResponse,
    summary="Получить тест для прохождения",
    description="""
    Публичный эндпоинт для получения теста по уникальному токену.
    
    **Доступ:**
    - Без авторизации
    - Любой человек с ссылкой может получить тест
    
    **Проверки:**
    - Тест существует
    - Срок доступа не истек (если указан)
    
    **Возвращает:**
    - Название теста
    - Поля профиля клиента (ФИО всегда обязательно)
    - Секции теста
    - Вопросы с вариантами ответов
    - Настройку видимости отчета для клиента
    
    **Не возвращает:**
    - Метрики и формулы расчета
    - Шаблоны отчетов
    - Информацию о психологе
    """,
    responses={
        200: {
            "description": "Тест найден и доступен",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Тест найден",
                        "data": {
                            "id": 1,
                            "title": "Тест на профориентацию",
                            "client_can_view_report": False,
                            "profile_fields": [
                                {
                                    "id": 1,
                                    "field_name": "Возраст",
                                    "field_type": "number",
                                    "is_required": True,
                                    "display_order": 1
                                }
                            ],
                            "sections": [
                                {
                                    "id": 1,
                                    "title": "Личные качества",
                                    "display_order": 1
                                }
                            ],
                            "questions": [
                                {
                                    "id": 1,
                                    "section_id": 1,
                                    "question_text": "Оцените свою коммуникабельность",
                                    "question_type": "rating_scale",
                                    "is_required": True,
                                    "display_order": 1,
                                    "settings": {"min": 1, "max": 10},
                                    "options": []
                                }
                            ]
                        },
                        "errors": None
                    }
                }
            }
        },
        404: {
            "description": "Тест не найден или срок доступа истек",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Тест с токеном abc123 не найден",
                        "data": None,
                        "errors": [{"field": "token", "message": "Тест с токеном abc123 не найден"}]
                    }
                }
            }
        }
    }
)
async def get_public_test_endpoint(
    token: str,
    session: AsyncSession = Depends(get_db)
):
    logger.info(
        "Public test endpoint called",
        operation="get_public_test_endpoint",
        token=token
    )
    
    try:
        result = await get_test_by_token_service(session, token)
        
        logger.info(
            "Public test retrieved successfully in endpoint",
            operation="get_public_test_endpoint",
            test_id=result["id"]
        )
        
        return create_success_response(
            message="Тест найден",
            data=result
        )
    
    except (TestNotFound, TestAccessDenied) as e:
        logger.warning(
            "Test not found or access denied",
            operation="get_public_test_endpoint",
            token=token,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=token,
            reason="Test not found or access expired"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in public test endpoint",
            operation="get_public_test_endpoint",
            token=token,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.post(
    "/tests/{token}/submit",
    response_model=SuccessResponse,
    summary="Отправить результаты теста",
    description="""
    Единый эндпоинт для отправки всех результатов прохождения теста.
    
    **Доступ:**
    - Без авторизации
    - Любой человек с ссылкой
    
    **Что отправляется:**
    - ФИО клиента (обязательно)
    - Данные профиля (возраст, город и т.д.)
    - Все ответы на вопросы
    
    **Что происходит:**
    - Создается attempt (попытка прохождения)
    - Сохраняются данные профиля
    - Сохраняются все ответы
    - Attempt помечается как завершенный
    - Инкрементируется счетчик прохождений
    
    **Проверки:**
    - Тест существует и не истек
    - Все обязательные поля профиля заполнены
    - Все вопросы принадлежат тесту
    - Опции принадлежат вопросам
    
    **Использование:**
    - Фронтенд собирает все данные в памяти
    - В конце отправляет одним запросом
    - Получает attempt_id и статус
    """,
    responses={
        200: {
            "description": "Тест успешно отправлен",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Результаты теста сохранены",
                        "data": {
                            "attempt_id": 123,
                            "test_id": 1,
                            "test_title": "Тест на профориентацию",
                            "client_name": "Иванов Иван Иванович",
                            "submitted_at": "2026-03-21T15:30:00",
                            "can_view_report": True,
                            "message": "Тест успешно завершен. Отчет доступен для просмотра"
                        },
                        "errors": None
                    }
                }
            }
        },
        400: {
            "description": "Ошибка валидации",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Не заполнены обязательные поля профиля",
                        "data": None,
                        "errors": [
                            {
                                "field": "profile_values",
                                "message": "Не заполнены обязательные поля профиля: Возраст, Город"
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Тест не найден или срок доступа истек"
        }
    }
)
async def submit_test_endpoint(
    token: str,
    submission: TestSubmission,
    session: AsyncSession = Depends(get_db)
):
    from app.services.test_submission_service import submit_test_service, SubmissionError
    
    logger.info(
        "Submit test endpoint called",
        operation="submit_test_endpoint",
        token=token,
        client_name=submission.client_name,
        answers_count=len(submission.answers)
    )
    
    try:
        result = await submit_test_service(session, token, submission)
        
        logger.info(
            "Test submitted successfully in endpoint",
            operation="submit_test_endpoint",
            attempt_id=result.attempt_id
        )
        
        return create_success_response(
            message="Результаты теста сохранены",
            data=result.model_dump()
        )
    
    except SubmissionError as e:
        logger.warning(
            "Test submission failed",
            operation="submit_test_endpoint",
            token=token,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=token,
            reason="Submission failed"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in submit test endpoint",
            operation="submit_test_endpoint",
            token=token,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
