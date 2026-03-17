from fastapi import Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.core.logging_config import get_logger
from app.database.crud.user_crud import create_user, get_user_by_tg_id
from app.database.models.users import User, AuthProviderEnum
from app.services.user import generate_auth_tokens
from app.schemas.telegram import TelegramLoginData
from sqlalchemy import select

logger = get_logger(__name__)


async def login_telegram_user(
        session: AsyncSession,
        tg_data: TelegramLoginData,
        response: Response
) -> dict:
    # 1. Формируем telegram_id (приводим к строке, так как в модели у нас str)
    telegram_id = str(tg_data.id)

    user = await get_user_by_tg_id(session, telegram_id)

    if not user:
        username = tg_data.username if tg_data.username else tg_data.first_name

        new_user = User(
            username=username,
            telegram_id=telegram_id,
            avatar_url=tg_data.photo_url,
            auth_provider=AuthProviderEnum.telegram,
            email_verified=True,
            is_admin=False
        )
        user = await create_user(session, new_user)
        logger.info(f"Created new user via Telegram: {username}")
    else:
        # Обновляем аватарку, если изменилась
        if tg_data.photo_url and user.avatar_url != tg_data.photo_url:
            user.avatar_url = tg_data.photo_url
            await session.commit()

    # 4. Генерируем токены
    access_token, refresh_token = generate_auth_tokens(user)

    # 5. Куки
    response.set_cookie(
        key="jwt",
        value=refresh_token,
        httponly=True,
        samesite="Strict",
        secure=True
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar_url
        }
    }
