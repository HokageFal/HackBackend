from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
from app.database.models.users import User
from app.database.core import AsyncSessionLocal
from app.core.security import verify_password
import logging

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    """Аутентификация для админ-панели"""
    
    async def login(self, request: Request) -> bool:
        """Обработка логина"""
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        
        logger.info(f"Попытка входа для email: {email}")
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.email == email).limit(1)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"Пользователь не найден: {email}")
                return False
            
            logger.info(f"Пользователь найден: {user.email}, is_admin: {user.is_admin}")
            
            if not user.password:
                logger.warning(f"У пользователя нет пароля: {email}")
                return False
            
            logger.info("Проверка пароля...")
            password_valid = verify_password(password, user.password)
            logger.info(f"Пароль валиден: {password_valid}")
            
            if not password_valid:
                logger.warning(f"Неверный пароль для пользователя: {email}")
                return False
            
            if not user.is_admin:
                logger.warning(f"Пользователь не является администратором: {email}")
                return False
            
            request.session.update({"user_id": user.id})
            logger.info(f"Успешный вход для пользователя: {email}")
            
        return True
    
    async def logout(self, request: Request) -> bool:
        """Обработка логаута"""
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        """Проверка аутентификации"""
        user_id = request.session.get("user_id")
        
        if not user_id:
            return False
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_admin:
                return False
            
        return True

