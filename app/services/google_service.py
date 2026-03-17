from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.database.crud.user_crud import get_user_by_google_id, get_user_by_email, update_user_google_data, create_user
from app.database.models.users import User, AuthProviderEnum
from app.services.user import generate_auth_tokens


async def login_google_user(session: AsyncSession, user_data: dict, response: Response) -> dict:

    logger = get_logger(__name__)
    logger.info("Starting Google login processing", email=user_data.get("email"))

    # 1. Получаем данные пользователя от Google
    google_id = user_data.get("sub")
    email = user_data.get("email")
    name = user_data.get("name", "Unknown User")
    picture = user_data.get("picture")

    # 2. Ищем пользователя по Google ID
    user = await get_user_by_google_id(session, google_id)
    if user:
        logger.info("Existing Google user found", user_id=user.id)
    else:
        # 3. Ищем пользователя по email (возможно зарегистрирован через email)
        if email:
            user = await get_user_by_email(session, email)
            if user:
                # Связываем существующий аккаунт с Google
                user = await update_user_google_data(session, user, google_id, picture)
                logger.info("Linked existing email user with Google", user_id=user.id)
            else:
                # 4. Создаем нового пользователя
                new_user = User(
                    email=email,
                    username=name,
                    password="",
                    google_id=google_id,
                    avatar_url=picture,
                    auth_provider=AuthProviderEnum.google,
                    email_verified=True,
                    is_admin=False
                )
                user = await create_user(session, new_user)
                logger.info("New Google user created", user_id=user.id)

    # 5. Генерируем токены
    access_token, refresh_token = generate_auth_tokens(user)

    # 6. Ставим Refresh токен в куки
    response.set_cookie(
        key="jwt",
        value=refresh_token,
        httponly=True,
        samesite="Strict",
        secure=True
    )

    logger.info("Google login successful", user_id=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url
        }
    }
