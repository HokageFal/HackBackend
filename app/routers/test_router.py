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
    description="Создает новый тест со всей структурой (секции, вопросы, опции, поля профиля, метрики, шаблоны)"
)
async def create_test_endpoint(
    test_data: dict,
    request: Request,
    session: AsyncSession = Depends(get_db)
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
    description="Получает список тестов психолога с пагинацией"
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
    description="Получает тест со всей структурой (секции, вопросы, опции, поля профиля, метрики, шаблоны)"
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
    description="Получает публичную ссылку на тест для клиентов"
)
async def get_test_link_endpoint(
    test_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        psychologist = await get_current_psychologist(request, session)
        
        test = await get_test_by_id_service(session, test_id, psychologist.id)
        
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        public_link = f"{base_url}/public/tests/{test.public_link_token}"
        
        return create_success_response(
            message="Публичная ссылка получена",
            data={
                "test_id": test.id,
                "title": test.title,
                "public_link": public_link,
                "public_link_token": test.public_link_token
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
