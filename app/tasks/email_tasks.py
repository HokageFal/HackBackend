from app.celery import celery_app
from app.core.logging_config import get_logger
from app.core.email_utils import send_email_sync, create_otp_email_template
from app.core.email_utils import create_password_reset_email_template
logger = get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.email_tasks.send_otp_email_task")
def send_otp_email_task(self, email: str, username: str, otp_code: str):
    task_id = self.request.id
    
    logger.info(
        "Starting OTP email task",
        operation="send_otp_email_task",
        task_id=task_id,
        email=email,
        username=username
    )
    
    try:
        email_body = create_otp_email_template(username, otp_code)

        send_email_sync(
            to_email=email,
            subject="Код подтверждения - AI Landing Generator",
            body=email_body,
            is_html=True
        )
        
        logger.info(
            "OTP email sent successfully",
            operation="send_otp_email_task",
            task_id=task_id,
            email=email,
            username=username
        )
        
        return {
            "status": "success",
            "message": f"OTP code sent to {email}",
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(
            "Failed to send OTP email",
            operation="send_otp_email_task",
            task_id=task_id,
            email=email,
            username=username,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )

        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.tasks.email_tasks.test_task")
def test_task(self):
    task_id = self.request.id
    
    logger.info(
        "Test task executed",
        operation="test_task",
        task_id=task_id
    )
    
    return {
        "status": "success",
        "message": "Test task completed",
        "task_id": task_id
    }


@celery_app.task(bind=True, name="app.tasks.email_tasks.send_password_reset_email_task")
def send_password_reset_email_task(self, email: str, username: str, otp_code: str):
    task_id = self.request.id
    
    logger.info(
        "Starting password reset email task",
        operation="send_password_reset_email_task",
        task_id=task_id,
        email=email,
        username=username
    )
    
    try:
        
        email_body = create_password_reset_email_template(username, otp_code)

        send_email_sync(
            to_email=email,
            subject="Сброс пароля - AI Landing Generator",
            body=email_body,
            is_html=True
        )
        
        logger.info(
            "Password reset email sent successfully",
            operation="send_password_reset_email_task",
            task_id=task_id,
            email=email,
            username=username
        )
        
        return {
            "status": "success",
            "message": f"Password reset code sent to {email}",
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(
            "Failed to send password reset email",
            operation="send_password_reset_email_task",
            task_id=task_id,
            email=email,
            username=username,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )

        raise self.retry(exc=e, countdown=60, max_retries=3)
