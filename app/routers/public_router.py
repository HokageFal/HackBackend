from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.response_utils import (
    create_success_response,
    create_server_error,
    create_not_found_error
)
from app.schemas.api_response import SuccessResponse
from app.schemas.test_attempt import AttemptCreate, AnswersSubmit
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
    "/tests/{token}/attempts",
    response_model=SuccessResponse,
    summary="Начать прохождение теста",
    description="""
    Создает новую попытку прохождения теста.
    
    **Доступ:**
    - Без авторизации
    - Любой человек с ссылкой может начать тест
    
    **Что происходит:**
    - Создается запись TestAttempt
    - Сохраняются данные профиля клиента (ФИО + доп поля)
    - Инкрементируется счетчик прохождений теста
    - Возвращается attempt_id для дальнейшей работы
    
    **Проверки:**
    - Тест существует
    - Срок доступа не истек
    - Все обязательные поля профиля заполнены
    - client_name не пустой (ФИО обязательно)
    
    **Важно:**
    - ФИО (client_name) всегда обязательно
    - Дополнительные поля профиля задаются психологом
    - После создания attempt_id используется для сохранения ответов
    """,
    responses={
        201: {
            "description": "Попытка создана успешно",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Прохождение теста начато",
                        "data": {
                            "attempt_id": 123,
                            "test_id": 1,
                            "test_title": "Тест на профориентацию",
                            "client_name": "Иванов Иван Иванович",
                            "started_at": "2026-03-21T10:30:00",
                            "total_questions": 25
                        },
                        "errors": None
                    }
                }
            }
        },
        400: {
            "description": "Ошибка валидации данных",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Не заполнены обязательные поля профиля",
                        "data": None,
                        "errors": [{"field": "profile_values", "message": "Не заполнены обязательные поля профиля: {1, 2}"}]
                    }
                }
            }
        },
        404: {
            "description": "Тест не найден или срок доступа истек"
        }
    }
)
async def create_attempt_endpoint(
    token: str,
    attempt_data: AttemptCreate,
    session: AsyncSession = Depends(get_db)
):
    from app.services.test_attempt_service import create_attempt_service, AttemptError
    
    logger.info(
        "Create attempt endpoint called",
        operation="create_attempt_endpoint",
        token=token
    )
    
    try:
        result = await create_attempt_service(session, token, attempt_data)
        
        logger.info(
            "Attempt created successfully in endpoint",
            operation="create_attempt_endpoint",
            attempt_id=result.attempt_id
        )
        
        return create_success_response(
            message="Прохождение теста начато",
            data=result.model_dump()
        )
    
    except AttemptError as e:
        logger.warning(
            "Attempt creation failed",
            operation="create_attempt_endpoint",
            token=token,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=token,
            reason="Attempt creation failed"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in create attempt endpoint",
            operation="create_attempt_endpoint",
            token=token,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.post(
    "/attempts/{attempt_id}/answers",
    response_model=SuccessResponse,
    summary="Сохранить ответы на вопросы",
    description="""
    Сохраняет ответы клиента на вопросы теста.
    
    **Доступ:**
    - Без авторизации
    - Требуется валидный attempt_id
    
    **Особенности:**
    - Можно вызывать многократно (сохранение по мере прохождения)
    - Можно отправить один или несколько ответов за раз
    - Повторная отправка ответа на тот же вопрос обновит его
    - Нельзя изменить ответы после завершения теста (submit)
    
    **Типы ответов:**
    - text_answer: для text, textarea
    - boolean_answer: для boolean
    - number_answer: для number, slider, rating_scale
    - datetime_answer: для datetime
    - selected_option_ids: для single_choice, multiple_choice
    
    **Проверки:**
    - Attempt существует и не завершен
    - Вопросы принадлежат тесту
    - Опции принадлежат вопросам
    - Тип ответа соответствует типу вопроса
    """,
    responses={
        200: {
            "description": "Ответы сохранены успешно",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Ответы сохранены",
                        "data": {
                            "saved": 3,
                            "updated": 1,
                            "total": 4
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
                        "message": "Тест уже завершен, нельзя изменить ответы",
                        "data": None,
                        "errors": [{"field": "attempt_id", "message": "Тест уже завершен, нельзя изменить ответы"}]
                    }
                }
            }
        },
        404: {
            "description": "Попытка не найдена"
        }
    }
)
async def save_answers_endpoint(
    attempt_id: int,
    answers_data: AnswersSubmit,
    session: AsyncSession = Depends(get_db)
):
    from app.services.test_attempt_service import save_answers_service, AttemptError
    
    logger.info(
        "Save answers endpoint called",
        operation="save_answers_endpoint",
        attempt_id=attempt_id,
        answers_count=len(answers_data.answers)
    )
    
    try:
        result = await save_answers_service(session, attempt_id, answers_data)
        
        logger.info(
            "Answers saved successfully in endpoint",
            operation="save_answers_endpoint",
            attempt_id=attempt_id,
            saved=result["saved"],
            updated=result["updated"]
        )
        
        return create_success_response(
            message="Ответы сохранены",
            data=result
        )
    
    except AttemptError as e:
        logger.warning(
            "Answer save failed",
            operation="save_answers_endpoint",
            attempt_id=attempt_id,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(attempt_id),
            reason="Answer save failed"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in save answers endpoint",
            operation="save_answers_endpoint",
            attempt_id=attempt_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "/attempts/{attempt_id}/progress",
    response_model=SuccessResponse,
    summary="Получить прогресс прохождения",
    description="""
    Возвращает информацию о прогрессе прохождения теста.
    
    **Доступ:**
    - Без авторизации
    - Требуется валидный attempt_id
    
    **Возвращает:**
    - Общее количество вопросов
    - Количество отвеченных вопросов
    - Процент прохождения
    - Список ID неотвеченных вопросов
    
    **Использование:**
    - Для отображения прогресс-бара
    - Для проверки какие вопросы еще не отвечены
    - Для валидации перед submit
    """,
    responses={
        200: {
            "description": "Прогресс получен",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Прогресс получен",
                        "data": {
                            "attempt_id": 123,
                            "total_questions": 25,
                            "answered_questions": 18,
                            "progress_percent": 72.0,
                            "unanswered_question_ids": [5, 12, 15, 20, 21, 23, 24]
                        },
                        "errors": None
                    }
                }
            }
        },
        404: {
            "description": "Попытка не найдена"
        }
    }
)
async def get_progress_endpoint(
    attempt_id: int,
    session: AsyncSession = Depends(get_db)
):
    from app.services.test_attempt_service import get_progress_service, AttemptError
    
    logger.info(
        "Get progress endpoint called",
        operation="get_progress_endpoint",
        attempt_id=attempt_id
    )
    
    try:
        result = await get_progress_service(session, attempt_id)
        
        logger.info(
            "Progress retrieved successfully in endpoint",
            operation="get_progress_endpoint",
            attempt_id=attempt_id,
            progress=result.progress_percent
        )
        
        return create_success_response(
            message="Прогресс получен",
            data=result.model_dump()
        )
    
    except AttemptError as e:
        logger.warning(
            "Progress retrieval failed",
            operation="get_progress_endpoint",
            attempt_id=attempt_id,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(attempt_id),
            reason="Progress retrieval failed"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get progress endpoint",
            operation="get_progress_endpoint",
            attempt_id=attempt_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=SuccessResponse,
    summary="Завершить прохождение теста",
    description="""
    Завершает прохождение теста и фиксирует результат.
    
    **Доступ:**
    - Без авторизации
    - Требуется валидный attempt_id
    
    **Что происходит:**
    - Устанавливается submitted_at = текущее время
    - Проверяется что все обязательные вопросы отвечены
    - После submit нельзя изменить ответы
    - Результаты становятся видны психологу
    
    **Проверки:**
    - Attempt существует
    - Тест еще не завершен
    - Все обязательные вопросы отвечены
    
    **Возвращает:**
    - Информацию о завершении
    - Флаг can_view_report (может ли клиент видеть отчет)
    - Если can_view_report=true, фронт может показать отчет
    """,
    responses={
        200: {
            "description": "Тест завершен успешно",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Тест завершен",
                        "data": {
                            "attempt_id": 123,
                            "submitted_at": "2026-03-21T11:45:00",
                            "can_view_report": True,
                            "message": "Тест успешно завершен. Отчет доступен для просмотра"
                        },
                        "errors": None
                    }
                }
            }
        },
        400: {
            "description": "Ошибка завершения",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Не отвечены обязательные вопросы",
                        "data": None,
                        "errors": [{"field": "answers", "message": "Не отвечены обязательные вопросы: {5, 12, 15}"}]
                    }
                }
            }
        },
        404: {
            "description": "Попытка не найдена"
        }
    }
)
async def submit_attempt_endpoint(
    attempt_id: int,
    session: AsyncSession = Depends(get_db)
):
    from app.services.test_attempt_service import submit_attempt_service, AttemptError
    
    logger.info(
        "Submit attempt endpoint called",
        operation="submit_attempt_endpoint",
        attempt_id=attempt_id
    )
    
    try:
        result = await submit_attempt_service(session, attempt_id)
        
        logger.info(
            "Attempt submitted successfully in endpoint",
            operation="submit_attempt_endpoint",
            attempt_id=attempt_id,
            submitted_at=result.submitted_at
        )
        
        return create_success_response(
            message="Тест завершен",
            data=result.model_dump()
        )
    
    except AttemptError as e:
        logger.warning(
            "Attempt submission failed",
            operation="submit_attempt_endpoint",
            attempt_id=attempt_id,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(attempt_id),
            reason="Attempt submission failed"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in submit attempt endpoint",
            operation="submit_attempt_endpoint",
            attempt_id=attempt_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
