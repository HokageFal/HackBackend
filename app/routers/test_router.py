from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.dependencies import get_current_psychologist, AccessDeniedError
from app.core.response_utils import (
    create_success_response,
    create_forbidden_error,
    create_server_error,
    create_not_found_error
)
from app.schemas.test import TestCreate, TestUpdate, TestResponse, TestLinkResponse, TestExportData
from app.schemas.api_response import SuccessResponse
from app.services.test_service import (
    create_test_service,
    get_tests_by_psychologist_service,
    get_test_by_id_service,
    update_test_service,
    delete_test_service,
    export_test_service,
    import_test_service,
    TestNotFound,
    TestAccessDenied
)
from app.core.logging_config import get_logger
import os

logger = get_logger(__name__)

router = APIRouter(prefix="/tests", tags=["Tests"])


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=201,
    summary="Создать тест",
    description="""
    Создает новый тест со всей структурой одним запросом.
    
    **Структура запроса:**
    - `test` - базовые настройки теста
    - `sections` - секции/разделы теста (опционально)
    - `questions` - вопросы с вариантами ответов
    - `profile_fields` - дополнительные поля профиля клиента (опционально)
    - `metrics` - формулы для расчета метрик (опционально)
    - `report_templates` - шаблоны отчетов (опционально)
    
    **Связи:**
    - Используйте `temp_id` в секциях для связи с вопросами
    - В вопросах указывайте `section_id` = `temp_id` секции
    - Варианты ответов (`options`) вкладываются прямо в вопрос
    
    **Типы вопросов:**
    
    1. **text** - Короткий текстовый ответ (одна строка)
       - Для имени, города, профессии и т.д.
       - Не требует options
       
    2. **textarea** - Многострочный текстовый ответ
       - Для развернутых ответов, эссе, описаний
       - Не требует options
       
    3. **single_choice** - Выбор одного варианта из списка (радиокнопки)
       - Требует options с вариантами ответов
       - Клиент выбирает только один вариант
       
    4. **multiple_choice** - Выбор нескольких вариантов (чекбоксы)
       - Требует options с вариантами ответов
       - Клиент может выбрать несколько вариантов
       
    5. **boolean** - Да/Нет вопрос
       - Простой выбор между двумя вариантами
       - Не требует options (автоматически Да/Нет)
       
    6. **number** - Числовой ответ
       - Для возраста, количества, процентов и т.д.
       - Можно указать min/max в settings
       
    7. **slider** - Ползунок с диапазоном значений
       - Для оценки по шкале
       - Требует settings: {"min": 0, "max": 100, "step": 1}
       
    8. **datetime** - Выбор даты и/или времени
       - Для даты рождения, времени события и т.д.
       - Можно указать формат в settings
       
    9. **rating_scale** - Шкала оценки (звездочки, баллы)
       - Для оценки от 1 до N
       - Требует settings: {"min": 1, "max": 10}
    """,
    responses={
        201: {
            "description": "Тест успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Тест успешно создан",
                        "data": {
                            "id": 1,
                            "title": "Тест на профориентацию",
                            "public_link_token": "abc123xyz",
                            "access_until": "2026-12-31T23:59:59",
                            "client_can_view_report": False,
                            "attempts_count": 0,
                            "sections": [
                                {
                                    "id": 1,
                                    "title": "Личные качества",
                                    "description": "Оцените свои качества",
                                    "display_order": 1
                                }
                            ],
                            "questions": [
                                {
                                    "id": 1,
                                    "section_id": 1,
                                    "question_text": "Как вы оцениваете свою коммуникабельность?",
                                    "question_type": "rating",
                                    "is_required": True,
                                    "display_order": 1,
                                    "settings": {"min": 1, "max": 10},
                                    "options": []
                                }
                            ],
                            "profile_fields": [],
                            "metrics": [],
                            "report_templates": []
                        },
                        "errors": None
                    }
                }
            }
        },
        401: {
            "description": "Не авторизован",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Токен не найден",
                        "data": None,
                        "errors": [{"field": "token", "message": "Токен не найден"}]
                    }
                }
            }
        },
        403: {
            "description": "Доступ запрещен (не психолог или заблокирован)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Доступ разрешен только психологам",
                        "data": None,
                        "errors": [{"field": "role", "message": "Доступ разрешен только психологам"}]
                    }
                }
            }
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Внутренняя ошибка сервера",
                        "data": None,
                        "errors": None
                    }
                }
            }
        }
    }
)
async def create_test_endpoint(
    request: Request,
    session: AsyncSession = Depends(get_db),
    test_data: dict = {
        "test": {
            "title": "Тест на профориентацию",
            "access_until": "2026-12-31T23:59:59",
            "client_can_view_report": False
        },
        "sections": [
            {
                "temp_id": "section1",
                "title": "Личные качества",
                "description": "Оцените свои личные качества",
                "display_order": 1
            }
        ],
        "questions": [
            {
                "temp_id": "q1",
                "section_id": "section1",
                "question_text": "Введите ваше имя",
                "question_type": "text",
                "is_required": True,
                "display_order": 1,
                "options": []
            },
            {
                "temp_id": "q2",
                "section_id": "section1",
                "question_text": "Расскажите о своих целях",
                "question_type": "textarea",
                "is_required": False,
                "display_order": 2,
                "options": []
            },
            {
                "temp_id": "q3",
                "section_id": "section1",
                "question_text": "Выберите ваш уровень образования",
                "question_type": "single_choice",
                "is_required": True,
                "display_order": 3,
                "options": [
                    {"option_text": "Среднее", "option_value": 1, "display_order": 1},
                    {"option_text": "Высшее", "option_value": 2, "display_order": 2},
                    {"option_text": "Магистратура", "option_value": 3, "display_order": 3}
                ]
            },
            {
                "temp_id": "q4",
                "section_id": "section1",
                "question_text": "Какие навыки у вас есть? (можно выбрать несколько)",
                "question_type": "multiple_choice",
                "is_required": False,
                "display_order": 4,
                "options": [
                    {"option_text": "Коммуникация", "option_value": 1, "display_order": 1},
                    {"option_text": "Лидерство", "option_value": 2, "display_order": 2},
                    {"option_text": "Аналитика", "option_value": 3, "display_order": 3},
                    {"option_text": "Креативность", "option_value": 4, "display_order": 4}
                ]
            },
            {
                "temp_id": "q5",
                "section_id": "section1",
                "question_text": "Вы готовы к переезду?",
                "question_type": "boolean",
                "is_required": True,
                "display_order": 5,
                "options": []
            },
            {
                "temp_id": "q6",
                "section_id": "section1",
                "question_text": "Сколько вам лет?",
                "question_type": "number",
                "is_required": True,
                "display_order": 6,
                "settings": {"min": 14, "max": 100},
                "options": []
            },
            {
                "temp_id": "q7",
                "section_id": "section1",
                "question_text": "Оцените вашу мотивацию к обучению",
                "question_type": "slider",
                "is_required": True,
                "display_order": 7,
                "settings": {"min": 0, "max": 100, "step": 10},
                "options": []
            },
            {
                "temp_id": "q8",
                "section_id": "section1",
                "question_text": "Когда вы планируете начать работу?",
                "question_type": "datetime",
                "is_required": False,
                "display_order": 8,
                "options": []
            },
            {
                "temp_id": "q9",
                "section_id": "section1",
                "question_text": "Оцените свою коммуникабельность",
                "question_type": "rating_scale",
                "is_required": True,
                "display_order": 9,
                "settings": {"min": 1, "max": 10},
                "options": []
            }
        ],
        "profile_fields": [
            {
                "field_name": "Возраст",
                "field_type": "number",
                "is_required": True,
                "display_order": 1
            }
        ],
        "metrics": [],
        "report_templates": []
    }
):
    logger.info(
        "Create test endpoint called",
        operation="create_test_endpoint"
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        result = await create_test_service(session, psychologist.id, test_data)
        
        logger.info(
            "Test created successfully in endpoint",
            operation="create_test_endpoint",
            test_id=result["id"]
        )
        
        return create_success_response(
            message="Тест успешно создан",
            data=result
        )
    
    except AccessDeniedError as e:
        logger.warning(
            "Access denied in create test",
            operation="create_test_endpoint",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in create test endpoint",
            operation="create_test_endpoint",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "",
    response_model=SuccessResponse,
    summary="Получить список тестов",
    description="""
    Получает список тестов психолога с пагинацией.
    
    **Параметры:**
    - `page` - номер страницы (по умолчанию 1)
    - `limit` - количество на странице (по умолчанию 20, макс 100)
    
    **Возвращает:**
    - Список тестов (краткая информация)
    - Информацию о пагинации
    """,
    responses={
        200: {
            "description": "Список тестов получен",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Найдено тестов: 15",
                        "data": {
                            "tests": [
                                {
                                    "id": 1,
                                    "title": "Тест на профориентацию",
                                    "public_link_token": "abc123xyz",
                                    "access_until": "2026-12-31T23:59:59",
                                    "client_can_view_report": False,
                                    "attempts_count": 5
                                },
                                {
                                    "id": 2,
                                    "title": "Тест на лидерство",
                                    "public_link_token": "def456uvw",
                                    "access_until": None,
                                    "client_can_view_report": True,
                                    "attempts_count": 12
                                }
                            ],
                            "pagination": {
                                "total": 15,
                                "page": 1,
                                "limit": 20,
                                "total_pages": 1,
                                "has_next": False,
                                "has_prev": False
                            }
                        },
                        "errors": None
                    }
                }
            }
        }
    }
)
async def get_tests_endpoint(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page: int = 1,
    limit: int = 20
):
    try:
        psychologist = await get_current_psychologist(request, session)
        
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        skip = (page - 1) * limit
        
        tests, total = await get_tests_by_psychologist_service(session, psychologist.id, skip, limit)
        
        tests_data = [
            {
                "id": t.id,
                "title": t.title,
                "public_link_token": t.public_link_token,
                "access_until": t.access_until.isoformat() if t.access_until else None,
                "client_can_view_report": t.client_can_view_report,
                "attempts_count": t.attempts_count
            }
            for t in tests
        ]
        
        total_pages = (total + limit - 1) // limit
        
        return create_success_response(
            message=f"Найдено тестов: {total}",
            data={
                "tests": tests_data,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get tests endpoint",
            operation="get_tests_endpoint",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "/{test_id}",
    response_model=SuccessResponse,
    summary="Получить тест",
    description="""
    Получает тест со всей структурой одним запросом.
    
    **Возвращает:**
    - Базовую информацию о тесте
    - Все секции
    - Все вопросы с вариантами ответов
    - Поля профиля клиента
    - Метрики и формулы
    - Шаблоны отчетов
    
    **Доступ:**
    - Только владелец теста (психолог, создавший тест)
    """,
    responses={
        200: {
            "description": "Тест найден",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Тест найден",
                        "data": {
                            "id": 1,
                            "title": "Тест на профориентацию",
                            "public_link_token": "abc123xyz",
                            "access_until": "2026-12-31T23:59:59",
                            "client_can_view_report": False,
                            "attempts_count": 5,
                            "sections": [
                                {
                                    "id": 1,
                                    "title": "Личные качества",
                                    "description": "Оцените свои качества",
                                    "display_order": 1
                                }
                            ],
                            "questions": [
                                {
                                    "id": 1,
                                    "section_id": 1,
                                    "question_text": "Как вы оцениваете свою коммуникабельность?",
                                    "question_type": "rating",
                                    "is_required": True,
                                    "display_order": 1,
                                    "settings": {"min": 1, "max": 10},
                                    "options": []
                                }
                            ],
                            "profile_fields": [],
                            "metrics": [],
                            "report_templates": []
                        },
                        "errors": None
                    }
                }
            }
        },
        404: {
            "description": "Тест не найден или нет доступа",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Тест с ID 999 не найден",
                        "data": None,
                        "errors": [{"field": "test_id", "message": "Тест с ID 999 не найден"}]
                    }
                }
            }
        }
    }
)
async def get_test_endpoint(
    test_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        psychologist = await get_current_psychologist(request, session)
        
        result = await get_test_by_id_service(session, test_id, psychologist.id)
        
        return create_success_response(
            message="Тест найден",
            data=result
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (TestNotFound, TestAccessDenied) as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(test_id),
            reason="Test not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get test endpoint",
            operation="get_test_endpoint",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.patch(
    "/{test_id}",
    response_model=SuccessResponse,
    summary="Обновить тест",
    description="Обновляет базовые настройки теста"
)
async def update_test_endpoint(
    test_id: int,
    test_data: TestUpdate,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        psychologist = await get_current_psychologist(request, session)
        
        test = await update_test_service(session, test_id, psychologist.id, test_data)
        
        return create_success_response(
            message="Тест успешно обновлен",
            data={
                "id": test.id,
                "title": test.title,
                "public_link_token": test.public_link_token,
                "access_until": test.access_until.isoformat() if test.access_until else None,
                "client_can_view_report": test.client_can_view_report,
                "attempts_count": test.attempts_count
            }
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (TestNotFound, TestAccessDenied) as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(test_id),
            reason="Test not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in update test endpoint",
            operation="update_test_endpoint",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.delete(
    "/{test_id}",
    response_model=SuccessResponse,
    summary="Удалить тест",
    description="Удаляет тест и все связанные данные"
)
async def delete_test_endpoint(
    test_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        psychologist = await get_current_psychologist(request, session)
        
        await delete_test_service(session, test_id, psychologist.id)
        
        return create_success_response(
            message="Тест успешно удален",
            data={"test_id": test_id}
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (TestNotFound, TestAccessDenied) as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(test_id),
            reason="Test not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in delete test endpoint",
            operation="delete_test_endpoint",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "/{test_id}/link",
    response_model=SuccessResponse,
    summary="Получить публичную ссылку",
    description="""
    Получает публичную ссылку на тест для отправки клиентам.
    
    **Ссылка содержит:**
    - Уникальный токен теста
    - Полный URL для прохождения
    
    **Использование:**
    - Скопируйте ссылку и отправьте клиенту
    - Клиент может пройти тест без регистрации
    """,
    responses={
        200: {
            "description": "Публичная ссылка получена",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Публичная ссылка получена",
                        "data": {
                            "test_id": 1,
                            "title": "Тест на профориентацию",
                            "public_link": "http://localhost:8000/public/tests/abc123xyz",
                            "public_link_token": "abc123xyz"
                        },
                        "errors": None
                    }
                }
            }
        }
    }
)
async def get_test_link_endpoint(
    test_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        psychologist = await get_current_psychologist(request, session)
        
        result = await get_test_by_id_service(session, test_id, psychologist.id)
        
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        public_link = f"{base_url}/public/tests/{result['public_link_token']}"
        
        return create_success_response(
            message="Публичная ссылка получена",
            data={
                "test_id": result["id"],
                "title": result["title"],
                "public_link": public_link,
                "public_link_token": result["public_link_token"]
            }
        )
    
    except AccessDeniedError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (TestNotFound, TestAccessDenied) as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(test_id),
            reason="Test not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get test link endpoint",
            operation="get_test_link_endpoint",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()



@router.get(
    "/{test_id}/export",
    response_model=SuccessResponse,
    summary="Экспортировать тест",
    description="Экспортирует тест со всей структурой в JSON"
)
async def export_test_endpoint(
    test_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    logger.info(
        "Export test endpoint called",
        operation="export_test_endpoint",
        test_id=test_id
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        export_data = await export_test_service(session, test_id, psychologist.id)
        
        logger.info(
            "Test exported successfully in endpoint",
            operation="export_test_endpoint",
            test_id=test_id
        )
        
        return create_success_response(
            message="Тест успешно экспортирован",
            data=export_data
        )
    
    except AccessDeniedError as e:
        logger.warning(
            "Access denied in export test",
            operation="export_test_endpoint",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except (TestNotFound, TestAccessDenied) as e:
        logger.warning(
            "Test not found or access denied in export",
            operation="export_test_endpoint",
            test_id=test_id,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(test_id),
            reason="Test not found or access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in export test endpoint",
            operation="export_test_endpoint",
            test_id=test_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.post(
    "/import",
    response_model=SuccessResponse,
    status_code=201,
    summary="Импортировать тест",
    description="Импортирует тест из JSON"
)
async def import_test_endpoint(
    import_data: dict,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    logger.info(
        "Import test endpoint called",
        operation="import_test_endpoint"
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        test = await import_test_service(session, psychologist.id, import_data)
        
        logger.info(
            "Test imported successfully in endpoint",
            operation="import_test_endpoint",
            test_id=test.id
        )
        
        return create_success_response(
            message="Тест успешно импортирован",
            data={
                "id": test.id,
                "title": test.title,
                "public_link_token": test.public_link_token,
                "access_until": test.access_until.isoformat() if test.access_until else None,
                "client_can_view_report": test.client_can_view_report,
                "attempts_count": test.attempts_count
            }
        )
    
    except AccessDeniedError as e:
        logger.warning(
            "Access denied in import test",
            operation="import_test_endpoint",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in import test endpoint",
            operation="import_test_endpoint",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
