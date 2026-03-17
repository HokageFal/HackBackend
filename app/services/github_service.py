from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.database.crud.user_crud import (
    get_user_by_github_id,
    get_user_by_email,
    create_user,
    update_user_github_data
)
from app.database.models.users import User, AuthProviderEnum
from app.services.user import generate_auth_tokens


async def login_github_user(session: AsyncSession, user_data: dict, response: Response) -> dict:
    logger = get_logger(__name__)
    logger.info("Starting GitHub login processing", email=user_data.get("email"))

    # Приводим к строке, чтобы база не ругалась, если поле VARCHAR
    github_id = str(user_data.get("id"))
    email = user_data.get("email")
    username = user_data.get("login")
    picture = user_data.get("avatar_url")

    # 1. Ищем по GitHub ID
    user = await get_user_by_github_id(session, github_id)

    if user:
        logger.info("Existing GitHub user found", user_id=user.id)
    else:
        # 2. Ищем пользователя по email (если он есть)
        if email:
            user = await get_user_by_email(session, email)
            if user:
                # Связываем существующего пользователя с GitHub
                user = await update_user_github_data(session, user, github_id, picture)
                logger.info("Linked existing email user with GitHub", user_id=user.id)
            else:
                # 3. Создаем нового пользователя с email
                new_user = User(
                    email=email,
                    username=username,
                    github_id=github_id,
                    avatar_url=picture,
                    auth_provider=AuthProviderEnum.github,
                    email_verified=True,
                    is_admin=False
                )
                user = await create_user(session, new_user)
                logger.info("New GitHub user created", user_id=user.id)
        else:
            # 4. Создаем пользователя БЕЗ email (если GitHub скрыл email)
            new_user = User(
                email=None,  # Разрешаем NULL если поле nullable
                username=username or f"github_{github_id}",  # Используем username или генерируем
                github_id=github_id,
                avatar_url=picture,
                auth_provider=AuthProviderEnum.github,
                email_verified=False,  # Нет email - не верифицирован
                is_admin=False
            )
            user = await create_user(session, new_user)
            logger.info("New GitHub user created without email", user_id=user.id)

    # 5. Генерируем токены
    access_token, refresh_token = generate_auth_tokens(user)

    # 6. Куки
    response.set_cookie(
        key="jwt",
        value=refresh_token,
        httponly=True,
        samesite="Strict",
        secure=True
    )

    logger.info("GitHub login successful", user_id=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "token_balance": user.token_balance
        }
    }
