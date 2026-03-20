"""
Psychologist router.
Endpoints for managing psychologists (admin only).
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.dependencies import check_is_admin, ForbiddenError
from app.core.response_utils import (
    create_success_response,
    create_conflict_error,
    create_forbidden_error,
    create_server_error
)
from app.schemas.psychologist import PsychologistCreate
from app.schemas.api_response import SuccessResponse
from app.services.psychologist_service import create_psychologist_service
from app.services.user.exceptions import UserAlreadyExists

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
    """
    Создание нового психолога администратором.
    
    - **full_name**: ФИО психолога (обязательно)
    - **email**: Email психолога (обязательно, уникальный)
    - **phone**: Телефон психолога (обязательно)
    - **password**: Пароль (обязательно, минимум 8 символов)
    - **access_until**: Дата окончания доступа (опционально)
    - **send_email**: Отправить данные на email психолога (по умолчанию true)
    """
    try:
        # Проверяем права администратора
        await check_is_admin(request, session)
        
        # Создаем психолога
        psychologist = await create_psychologist_service(session, psychologist_data)
        
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
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Admin access required"
        )
    
    except UserAlreadyExists as e:
        raise create_conflict_error(
            field=e.field,
            message=e.message,
            input_data=psychologist_data.email,
            reason="Email already exists"
        )
    
    except Exception:
        raise create_server_error()
