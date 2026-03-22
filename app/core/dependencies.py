"""
FastAPI dependencies.
"""

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.core.csrf_utils import verify_csrf_token
from app.core.auth_utils import get_user_id_from_token
from app.core.timezone_utils import get_current_msk_time
from app.database.core import get_db
from app.database.crud.user_crud import get_user_by_id
from app.database.models.users import User, UserRoleEnum


async def verify_csrf(request: Request) -> bool:
    return verify_csrf_token(request)


class ForbiddenError(Exception):
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


class AccessDeniedError(Exception):
    
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



async def get_current_user(request: Request, session: AsyncSession = Depends(get_db)) -> User:
    user_id = get_user_id_from_token(request)
    
    user = await get_user_by_id(session, user_id)
    
    if not user:
        raise ForbiddenError(
            field="user_id",
            message="Пользователь не найден"
        )
    
    return user


async def get_current_active_user(request: Request, session: AsyncSession = Depends(get_db)) -> User:
    user = await get_current_user(request, session)
    
    if user.is_admin:
        return user
    
    if user.is_blocked:
        raise AccessDeniedError(
            field="is_blocked",
            message="Ваш аккаунт заблокирован. Обратитесь к администратору"
        )
    
    return user


async def get_current_psychologist(request: Request, session: AsyncSession = Depends(get_db)) -> User:
    user = await get_current_user(request, session)
    
    if user.role != UserRoleEnum.psychologist:
        raise ForbiddenError(
            field="role",
            message="Доступ разрешен только психологам"
        )
    
    if user.is_blocked:
        raise AccessDeniedError(
            field="is_blocked",
            message="Ваш аккаунт заблокирован. Обратитесь к администратору"
        )
    
    if user.access_until is not None:
        now = get_current_msk_time()
        if user.access_until < now:
            raise AccessDeniedError(
                field="access_until",
                message=f"Срок доступа истек {user.access_until.isoformat()}. Обратитесь к администратору"
            )
    
    return user


async def get_current_admin(request: Request, session: AsyncSession = Depends(get_db)) -> User:
    user = await get_current_user(request, session)
    
    if not user.is_admin:
        raise ForbiddenError(
            field="is_admin",
            message="Доступ запрещен. Требуются права администратора"
        )
    
    return user
