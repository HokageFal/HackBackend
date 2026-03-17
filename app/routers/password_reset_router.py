from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.response_utils import (
    create_success_response,
    create_business_logic_error,
    create_server_error
)
from app.schemas.password_reset import PasswordResetRequest, PasswordResetVerify
from app.schemas.api_response import SuccessResponse
from app.services.user.password_reset_service import request_password_reset, reset_password
from app.services.user.exceptions import UserNotFound, InvalidOperation
from app.core.logging_config import get_logger
from app.docs.password_reset_responses import (
    PASSWORD_RESET_REQUEST_RESPONSES,
    PASSWORD_RESET_VERIFY_RESPONSES
)

logger = get_logger(__name__)

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])


@router.post(
    "/request",
    response_model=SuccessResponse,
    status_code=200,
    responses=PASSWORD_RESET_REQUEST_RESPONSES,
)
async def request_password_reset_endpoint(
    reset_request: PasswordResetRequest,
    session: AsyncSession = Depends(get_db)
):
    try:
        result = await request_password_reset(session, reset_request.email)
        
        logger.info(
            "Password reset request processed",
            operation="request_password_reset_endpoint",
            email=reset_request.email
        )
        
        return create_success_response(
            message=result["message"],
            data={"email": reset_request.email}
        )
        
    except Exception as e:
        logger.error(
            "Failed to process password reset request",
            operation="request_password_reset_endpoint",
            email=reset_request.email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.post(
    "/verify",
    response_model=SuccessResponse,
    status_code=200,
    responses=PASSWORD_RESET_VERIFY_RESPONSES,
)
async def verify_password_reset_endpoint(
    reset_verify: PasswordResetVerify,
    session: AsyncSession = Depends(get_db)
):
    try:
        result = await reset_password(
            session,
            reset_verify.email,
            reset_verify.code,
            reset_verify.new_password
        )
        
        if not result["success"]:
            if "истек" in result["message"] or "не найден" in result["message"]:
                raise create_business_logic_error(
                    message=result["message"],
                    field="code",
                    input_data=reset_verify.code,
                    reason="Code not found or expired"
                )
            else:
                raise create_business_logic_error(
                    message=result["message"],
                    field="code",
                    input_data=reset_verify.code,
                    reason="Invalid verification code"
                )
        
        logger.info(
            "Password reset successful",
            operation="verify_password_reset_endpoint",
            email=reset_verify.email
        )
        
        return create_success_response(
            message=result["message"],
            data={"email": reset_verify.email}
        )
        
    except UserNotFound as e:
        logger.warning(
            "Password reset failed - user not found",
            operation="verify_password_reset_endpoint",
            email=reset_verify.email,
            reason="user_not_found"
        )
        raise create_business_logic_error(
            message=e.message,
            field=e.field,
            input_data=reset_verify.email,
            reason="User not found"
        )
    except InvalidOperation as e:
        logger.warning(
            "Password reset failed - invalid operation",
            operation="verify_password_reset_endpoint",
            email=reset_verify.email,
            reason="oauth_user"
        )
        raise create_business_logic_error(
            message=e.message,
            field=e.field,
            input_data=reset_verify.email,
            reason="Invalid operation for OAuth user"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to verify password reset",
            operation="verify_password_reset_endpoint",
            email=reset_verify.email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
