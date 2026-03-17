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
    """
    Dependency для проверки CSRF токена.
    
    Использование:
        @router.post("/endpoint", dependencies=[Depends(verify_csrf)])
        async def endpoint():
            ...
    """
    return verify_csrf_token(request)


class ForbiddenError(Exception):
    """Raised when user doesn't have required permissions."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


async def check_is_admin(request: Request, session: AsyncSession) -> bool:
    """
    Проверить является ли пользователь администратором.
    
    Args:
        request: FastAPI Request
        session: Сессия БД
        
    Returns:
        bool: True если админ
        
    Raises:
        ForbiddenError: Если пользователь не админ
        
    Использование в endpoint:
        @router.post("/admin/something")
        async def admin_endpoint(
            request: Request,
            session: AsyncSession = Depends(get_db)
        ):
            await check_is_admin(request, session)
            # Дальше логика для админа
            ...
    """
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
