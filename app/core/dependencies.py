"""
FastAPI dependencies.
"""

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.csrf_utils import verify_csrf_token
from app.core.auth_utils import get_user_id_from_token
from app.database.core import get_db
from app.database.crud.user_crud import get_user_by_id


async def verify_csrf(request: Request) -> bool:
    return verify_csrf_token(request)


class ForbiddenError(Exception):
    """Raised when user doesn't have required permissions."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


async def check_is_admin(request: Request, session: AsyncSession) -> bool:
    # Получаем ID пользователя из токена
    user_id = get_user_id_from_token(request)
    
    # Получаем пользователя из БД
    user = await get_user_by_id(session, user_id)
    
    if not user:
        raise ForbiddenError(
            field="user_id",
            message="Пользователь не найден"
        )
    
    # Проверяем права администратора
    if not user.is_admin:
        raise ForbiddenError(
            field="is_admin",
            message="Доступ запрещен. Требуются права администратора"
        )
    
    return True
