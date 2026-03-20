from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.dependencies import check_is_admin, ForbiddenError
from app.core.response_utils import (
    create_success_response,
    create_conflict_error,
    create_forbidden_error,
    create_server_error,
    create_not_found_error,
    create_business_logic_error
)
from app.schemas.psychologist import PsychologistCreate, PsychologistUpdate
from app.schemas.api_response import SuccessResponse
from app.services.psychologist_service import (
    create_psychologist_service,
    get_psychologist_by_id_service,
    get_all_psychologists_service,
    update_psychologist_service
)
from app.services.user.exceptions import UserAlreadyExists, UserNotFound
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/psychologists", tags=["Admin - Psychologists"])


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=201,
    summary="Создать психолога",
    description="Создает нового психолога. Доступно только администраторам."
)
async def create_psychologist_endpoint(
    psychologist_data: PsychologistCreate,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    logger.info(
        "Create psychologist endpoint called",
        operation="create_psychologist_endpoint",
        email=psychologist_data.email,
        full_name=psychologist_data.full_name
    )
    
    try:
        # Проверяем права администратора
        await check_is_admin(request, session)
        
        logger.info(
            "Admin check passed",
            operation="create_psychologist_endpoint"
        )
        
        # Создаем психолога
        psychologist = await create_psychologist_service(session, psychologist_data)
        
        logger.info(
            "Psychologist created successfully in endpoint",
            operation="create_psychologist_endpoint",
            psychologist_id=psychologist.id
        )
        
        return create_success_response(
            message="Психолог успешно создан",
            data={
                "id": psychologist.id,
                "full_name": psychologist.full_name,
                "email": psychologist.email,
                "phone": psychologist.phone,
                "access_until": psychologist.access_until.isoformat() if psychologist.access_until else None,
                "email_sent": psychologist_data.send_email
            }
        )
    
    except ForbiddenError as e:
        logger.warning(
            "Forbidden error in create psychologist",
            operation="create_psychologist_endpoint",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Admin access required"
        )
    
    except UserAlreadyExists as e:
        logger.warning(
            "User already exists error",
            operation="create_psychologist_endpoint",
            field=e.field,
            message=e.message
        )
        raise create_conflict_error(
            field=e.field,
            message=e.message,
            input_data=psychologist_data.email,
            reason="Email already exists"
        )
    
    except Exception as e:
        # Пробрасываем HTTPException (например, 401 от check_is_admin)
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in create psychologist endpoint",
            operation="create_psychologist_endpoint",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "",
    response_model=SuccessResponse,
    summary="Получить список всех психологов",
    description="Получает список всех психологов. Доступно только администраторам."
)
async def get_all_psychologists_endpoint(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        await check_is_admin(request, session)
        
        psychologists = await get_all_psychologists_service(session)
        
        psychologists_data = [
            {
                "id": p.id,
                "full_name": p.full_name,
                "email": p.email,
                "phone": p.phone,
                "role": p.role,
                "access_until": p.access_until.isoformat() if p.access_until else None,
                "is_blocked": p.is_blocked,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in psychologists
        ]
        
        return create_success_response(
            message=f"Найдено психологов: {len(psychologists)}",
            data={"psychologists": psychologists_data, "count": len(psychologists)}
        )
    
    except ForbiddenError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Admin access required"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get all psychologists endpoint",
            operation="get_all_psychologists_endpoint",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.get(
    "/{psychologist_id}",
    response_model=SuccessResponse,
    summary="Получить психолога по ID",
    description="Получает данные психолога по ID. Доступно только администраторам."
)
async def get_psychologist_endpoint(
    psychologist_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        await check_is_admin(request, session)
        
        psychologist = await get_psychologist_by_id_service(session, psychologist_id)
        
        return create_success_response(
            message="Психолог найден",
            data={
                "id": psychologist.id,
                "full_name": psychologist.full_name,
                "email": psychologist.email,
                "phone": psychologist.phone,
                "role": psychologist.role,
                "access_until": psychologist.access_until.isoformat() if psychologist.access_until else None,
                "is_blocked": psychologist.is_blocked,
                "created_at": psychologist.created_at.isoformat() if psychologist.created_at else None
            }
        )
    
    except ForbiddenError as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Admin access required"
        )
    
    except UserNotFound as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(psychologist_id),
            reason="Psychologist not found"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get psychologist endpoint",
            operation="get_psychologist_endpoint",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()



@router.patch(
    "/{psychologist_id}",
    response_model=SuccessResponse,
    summary="Обновить данные психолога",
    description="Обновляет данные психолога. Можно обновить любые поля. Доступно только администраторам."
)
async def update_psychologist_endpoint(
    psychologist_id: int,
    psychologist_update: PsychologistUpdate,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    logger.info(
        "Update psychologist endpoint called",
        operation="update_psychologist_endpoint",
        psychologist_id=psychologist_id
    )
    
    try:
        await check_is_admin(request, session)
        
        update_data = psychologist_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise create_business_logic_error(
                message="Необходимо указать хотя бы одно поле для обновления",
                field="body",
                input_data={},
                reason="No fields to update"
            )
        
        psychologist = await update_psychologist_service(session, psychologist_id, update_data)
        
        logger.info(
            "Psychologist updated successfully in endpoint",
            operation="update_psychologist_endpoint",
            psychologist_id=psychologist.id
        )
        
        return create_success_response(
            message="Психолог успешно обновлен",
            data={
                "id": psychologist.id,
                "full_name": psychologist.full_name,
                "email": psychologist.email,
                "phone": psychologist.phone,
                "role": psychologist.role,
                "access_until": psychologist.access_until.isoformat() if psychologist.access_until else None,
                "is_blocked": psychologist.is_blocked,
                "created_at": psychologist.created_at.isoformat() if psychologist.created_at else None
            }
        )
    
    except ForbiddenError as e:
        logger.warning(
            "Forbidden error in update psychologist",
            operation="update_psychologist_endpoint",
            psychologist_id=psychologist_id,
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Admin access required"
        )
    
    except UserNotFound as e:
        logger.warning(
            "Psychologist not found error",
            operation="update_psychologist_endpoint",
            psychologist_id=psychologist_id,
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=str(psychologist_id),
            reason="Psychologist not found"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in update psychologist endpoint",
            operation="update_psychologist_endpoint",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
