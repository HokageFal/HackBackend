from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.response_utils import (
    create_otp_response,
    create_rate_limit_error,
    create_business_logic_error,
    create_not_found_error,
    create_server_error
)
from app.schemas.otp_request import OTPRequest, OTPVerify
from app.schemas.api_response import OtpResponse
from app.services.otp_service import OTPService
from app.tasks.email_tasks import send_otp_email_task
from app.core.logging_config import get_logger
from app.docs.otp_responses import OTP_SEND_RESPONSES, OTP_VERIFY_RESPONSES
from app.services.user import activate_user_by_email, UserNotFound

logger = get_logger(__name__)

router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post(
    "/send",
    response_model=OtpResponse,
    status_code=200,
    responses=OTP_SEND_RESPONSES,
)
async def send_otp_code(otp_request: OTPRequest):

    try:
        # Проверяем rate limiting
        can_send = await OTPService.check_rate_limit(otp_request.email)
        if not can_send:
            raise create_rate_limit_error(
                field="email",
                message="Слишком частые запросы. Попробуйте через 1 минуту",
                input_data=otp_request.email,
                retry_after=60
            )
        
        # Генерируем OTP код
        otp_code = OTPService.generate_otp_code()
        
        # Сохраняем код в Redis
        await OTPService.save_otp_code(otp_request.email, otp_code)
        
        # Отправляем email через Celery
        send_otp_email_task.delay(
            email=otp_request.email,
            username=otp_request.email.split('@')[0],  # Используем часть email как имя
            otp_code=otp_code
        )
        
        logger.info(
            "OTP code sent successfully",
            operation="send_otp_code",
            email=otp_request.email
        )
        
        return create_otp_response(
            message="Код подтверждения отправлен на email",
            email=otp_request.email,
            expires_in_seconds=600  # 10 минут
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to send OTP code",
            operation="send_otp_code",
            email=otp_request.email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.post(
    "/verify",
    response_model=OtpResponse,
    status_code=200,
    responses=OTP_VERIFY_RESPONSES,
)
async def verify_otp_code(otp_verify: OTPVerify, session: AsyncSession = Depends(get_db)):
    try:
        # Проверяем OTP код
        result = await OTPService.verify_otp_code(otp_verify.email, otp_verify.code)
        
        if not result["success"]:
            if "истек" in result["message"] or "не найден" in result["message"]:
                raise create_not_found_error(
                    field="code",
                    message=result["message"],
                    input_data=otp_verify.code,
                    reason="Verification code not found or expired"
                )
            else:
                raise create_business_logic_error(
                    message=result["message"],
                    field="code",
                    input_data=otp_verify.code,
                    reason="Invalid verification code" if "Неверный" in result["message"] else "Max verification attempts exceeded"
                )
        
        # Активируем пользователя после успешной проверки OTP
        try:
            await activate_user_by_email(session, otp_verify.email)
        except UserNotFound as e:
            logger.warning(
                "User not found during activation",
                operation="verify_otp_code",
                email=otp_verify.email,
                reason="user_not_found"
            )
            # Продолжаем выполнение - OTP код был верный, но пользователь не найден
            # Это может произойти если пользователь был удален после отправки кода
        
        logger.info(
            "OTP code verified successfully",
            operation="verify_otp_code",
            email=otp_verify.email
        )
        
        return create_otp_response(
            message="Email успешно подтвержден",
            email=otp_verify.email,
            verified=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to verify OTP code",
            operation="verify_otp_code",
            email=otp_verify.email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
