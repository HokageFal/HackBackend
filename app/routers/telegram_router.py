import os
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.core import get_db
from app.schemas.telegram import TelegramLoginData
from app.core.telegram_utils import verify_telegram_data
from app.services.telegram_service import login_telegram_user
from app.core.response_utils import create_auth_success_response

router = APIRouter(prefix="/auth")


@router.get("/telegram/callback")
async def telegram_callback(
        response: Response,
        tg_data: TelegramLoginData = Depends(),
        db: AsyncSession = Depends(get_db)
):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN_DEV")

    if not bot_token:
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN_DEV is None! Check .env")
        raise HTTPException(status_code=500, detail="Server config error: No Bot Token")

    telegram_data_dict = tg_data.dict()
    clean_data = {k: v for k, v in telegram_data_dict.items() if v is not None}

    print(f"DEBUG: Checking signature with token ending in ...{bot_token[-5:]}")
    print(f"DEBUG: Data to check: {clean_data}")

    if not verify_telegram_data(clean_data, bot_token):
        print("DEBUG: Signature verification FAILED")
        raise HTTPException(status_code=400, detail="Invalid Telegram signature")

    auth_result = await login_telegram_user(db, tg_data, response)
    
    return create_auth_success_response(
        message="Вход через Telegram выполнен успешно",
        access_token=auth_result["access_token"],
        user_data=auth_result.get("user")
    )

