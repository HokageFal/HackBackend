import hashlib
import hmac
import time
from fastapi import HTTPException
from app.core.config import settings # Или os.getenv

def verify_telegram_data(data: dict, bot_token: str) -> bool:
    received_hash = data.get("hash")
    if not received_hash:
        return False

    # 1. Удаляем hash из данных, чтобы он не участвовал в подписи
    data_copy = data.copy()
    data_copy.pop("hash", None)

    # 2. Сортируем ключи по алфавиту и собираем строку "key=value"
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data_copy.items()))

    # 3. Создаем секретный ключ (SHA256 от токена бота)
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    # 4. Вычисляем HMAC-SHA256
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    # 5. Проверяем срок действия (опционально, например, ссылка живет 5 минут)
    auth_date = int(data.get("auth_date", 0))
    if time.time() - auth_date > 86400: # Данные устарели (больше суток)
        raise HTTPException(status_code=400, detail="Telegram auth date expired")

    # 6. Сравниваем хеши
    return calculated_hash == received_hash