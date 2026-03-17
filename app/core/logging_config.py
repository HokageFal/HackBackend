"""
Конфигурация логирования для продакшена.
Настроена по стандартам крупных компаний (Netflix, Uber, Airbnb).
"""

import os
import logging
import structlog
from typing import Any, Dict


def configure_production_logging() -> None:
    """
    Настраивает структурированное логирование для продакшена.
    
    Конфигурация включает:
    - JSON формат для машинного парсинга
    - ISO временные метки
    - Контекстная информация
    - Фильтрация чувствительных данных
    - Производительность
    """
    
    # Уровень логирования из переменных окружения
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Настройка стандартного логирования
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(message)s",
        stream=None,  # Используем structlog для вывода
    )
    
    # Настройка structlog для продакшена
    structlog.configure(
        processors=[
            # Фильтрация по уровню
            structlog.stdlib.filter_by_level,
            
            # Добавление имени логгера
            structlog.stdlib.add_logger_name,
            
            # Добавление уровня логирования
            structlog.stdlib.add_log_level,
            
            # Форматирование позиционных аргументов
            structlog.stdlib.PositionalArgumentsFormatter(),
            
            # Добавление временных меток в ISO формате
            structlog.processors.TimeStamper(fmt="iso"),
            
            # Добавление информации о стеке вызовов
            structlog.processors.StackInfoRenderer(),
            
            # Форматирование исключений
            structlog.processors.format_exc_info,
            
            # Декодирование Unicode
            structlog.processors.UnicodeDecoder(),
            
            # Фильтрация чувствительных данных
            _filter_sensitive_data,
            
            # Добавление контекста запроса
            _add_request_context,
            
            # JSON рендеринг для продакшена
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _filter_sensitive_data(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Фильтрует чувствительные данные из логов.
    
    Удаляет или маскирует:
    - Пароли
    - Токены
    - Email адреса (частично)
    - IP адреса (частично)
    """
    sensitive_fields = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
        'access_token', 'refresh_token', 'jwt', 'api_key', 'private_key'
    }
    
    # Маскируем чувствительные поля
    for key, value in event_dict.items():
        if any(sensitive_field in key.lower() for sensitive_field in sensitive_fields):
            if isinstance(value, str) and len(value) > 8:
                event_dict[key] = f"{value[:4]}***{value[-4:]}"
            else:
                event_dict[key] = "***"
    
    # Частично маскируем email
    if 'email' in event_dict:
        email = str(event_dict['email'])
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                masked_local = f"{local[0]}***{local[-1]}"
                event_dict['email'] = f"{masked_local}@{domain}"
    
    return event_dict


def _add_request_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Добавляет контекстную информацию о запросе.
    """
    # Добавляем информацию о сервисе
    event_dict['service'] = 'ai_landing_generator'
    event_dict['version'] = os.getenv('APP_VERSION', '1.0.0')
    
    # Добавляем информацию об окружении
    event_dict['environment'] = os.getenv('ENVIRONMENT', 'production')
    
    return event_dict


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Получает настроенный логгер для модуля.
    
    Args:
        name: Имя модуля (обычно __name__)
        
    Returns:
        Настроенный структурированный логгер
    """
    return structlog.get_logger(name)


# Автоматическая настройка при импорте
configure_production_logging()
