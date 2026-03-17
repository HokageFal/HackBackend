import redis
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Redis клиент
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


class OTPService:
    """Сервис для работы с OTP кодами."""
    
    @staticmethod
    def generate_otp_code() -> str:
        """Генерирует 6-значный OTP код."""
        return ''.join(random.choices(string.digits, k=settings.OTP_CODE_LENGTH))
    
    @staticmethod
    def get_otp_key(email: str) -> str:
        """Возвращает ключ для хранения OTP в Redis."""
        return f"otp:{email}"
    
    @staticmethod
    def get_rate_limit_key(email: str) -> str:
        """Возвращает ключ для rate limiting в Redis."""
        return f"otp_rate_limit:{email}"
    
    @classmethod
    async def save_otp_code(cls, email: str, code: str) -> None:
        """
        Сохраняет OTP код в Redis с TTL.
        
        Args:
            email: Email пользователя
            code: OTP код
        """
        logger.info(
            "Saving OTP code",
            operation="save_otp_code",
            email=email,
            code_length=len(code)
        )
        
        otp_key = cls.get_otp_key(email)
        otp_data = {
            "code": code,
            "attempts": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
        }
        
        # Сохраняем с TTL
        redis_client.hset(otp_key, mapping=otp_data)
        redis_client.expire(otp_key, settings.OTP_EXPIRE_MINUTES * 60)
        
        logger.info(
            "OTP code saved successfully",
            operation="save_otp_code",
            email=email,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES
        )
    
    @classmethod
    async def verify_otp_code(cls, email: str, code: str) -> Dict[str, Any]:
        """
        Проверяет OTP код.
        
        Args:
            email: Email пользователя
            code: OTP код для проверки
            
        Returns:
            Dict с результатом проверки
        """
        logger.info(
            "Verifying OTP code",
            operation="verify_otp_code",
            email=email,
            code_length=len(code)
        )
        
        otp_key = cls.get_otp_key(email)
        otp_data = redis_client.hgetall(otp_key)
        
        if not otp_data:
            logger.warning(
                "OTP code not found or expired",
                operation="verify_otp_code",
                email=email,
                reason="code_not_found"
            )
            return {
                "success": False,
                "message": "Код не найден или истек",
                "attempts_left": 0
            }
        
        # Проверяем количество попыток
        attempts = int(otp_data.get("attempts", 0))
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            logger.warning(
                "OTP max attempts exceeded",
                operation="verify_otp_code",
                email=email,
                attempts=attempts
            )
            # Удаляем код после превышения попыток
            redis_client.delete(otp_key)
            return {
                "success": False,
                "message": "Превышено максимальное количество попыток",
                "attempts_left": 0
            }
        
        # Проверяем код
        stored_code = otp_data.get("code")
        if stored_code != code:
            # Увеличиваем счетчик попыток
            attempts += 1
            redis_client.hset(otp_key, "attempts", attempts)
            
            logger.warning(
                "OTP code verification failed",
                operation="verify_otp_code",
                email=email,
                attempts=attempts,
                attempts_left=settings.OTP_MAX_ATTEMPTS - attempts
            )
            
            return {
                "success": False,
                "message": "Неверный код",
                "attempts_left": settings.OTP_MAX_ATTEMPTS - attempts
            }
        
        # Код верный - удаляем из Redis
        redis_client.delete(otp_key)
        
        logger.info(
            "OTP code verified successfully",
            operation="verify_otp_code",
            email=email
        )
        
        return {
            "success": True,
            "message": "Код подтвержден",
            "attempts_left": 0
        }
    
    @classmethod
    async def check_rate_limit(cls, email: str) -> bool:
        """
        Проверяет rate limiting для отправки OTP.
        
        Args:
            email: Email пользователя
            
        Returns:
            True если можно отправить, False если нужно подождать
        """
        rate_limit_key = cls.get_rate_limit_key(email)
        
        # Проверяем существование ключа
        if redis_client.exists(rate_limit_key):
            logger.warning(
                "Rate limit exceeded",
                operation="check_rate_limit",
                email=email
            )
            return False
        
        # Устанавливаем блокировку на указанное время
        redis_client.setex(rate_limit_key, settings.OTP_RATE_LIMIT_MINUTES * 60, "1")
        
        logger.info(
            "Rate limit check passed",
            operation="check_rate_limit",
            email=email
        )
        
        return True
    
    @classmethod
    async def cleanup_expired_codes(cls) -> int:
        """
        Очищает истекшие OTP коды (вызывается периодически).
        
        Returns:
            Количество удаленных кодов
        """
        logger.info(
            "Starting OTP cleanup",
            operation="cleanup_expired_codes"
        )
        
        # Redis автоматически удаляет ключи с истекшим TTL
        # Эта функция может быть расширена для дополнительной логики
        
        logger.info(
            "OTP cleanup completed",
            operation="cleanup_expired_codes"
        )
        
        return 0
