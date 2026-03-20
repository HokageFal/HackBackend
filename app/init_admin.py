"""
Автоматическое создание администратора при запуске приложения.
"""
print("=" * 70)
print("📦 МОДУЛЬ init_admin.py ЗАГРУЖАЕТСЯ!")
print("=" * 70)

import asyncio
import secrets
import string

print("✅ Базовые импорты OK")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
print("✅ SQLAlchemy импорты OK")

from app.core.config import settings
print("✅ Config импорт OK")

from app.core.security import hash_password
print("✅ Security импорт OK")

from app.database.models.users import User, UserRoleEnum
print("✅ Models импорт OK")

print("=" * 70)
print("✅ ВСЕ ИМПОРТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
print("=" * 70)


def generate_random_password(length: int = 16) -> str:
    """Генерирует безопасный случайный пароль."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_admin_email() -> str:
    """Генерирует email для админа с префиксом admin."""
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    return f"admin{random_suffix}@profdna.ru"


async def init_admin():
    """Проверяет и создает администратора если его нет."""
    
    print("\n" + "=" * 70)
    print("🚀 ФУНКЦИЯ init_admin() ВЫЗВАНА!")
    print("=" * 70)
    
    max_retries = 5
    retry_delay = 2  # секунды
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔍 Попытка {attempt}/{max_retries}: Проверка наличия администратора...")
            
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                result = await session.execute(select(User).where(User.role == UserRoleEnum.admin))
                existing_admin = result.scalars().first()
                
                if existing_admin:
                    print("✅ Администратор уже существует в базе данных")
                    print(f"   Email: {existing_admin.email}")
                    print(f"   ID: {existing_admin.id}")
                    await engine.dispose()
                    return
                
                print("📝 Администратор не найден. Создаем нового...")
                
                admin_email = generate_admin_email()
                admin_password = generate_random_password(16)
                admin_full_name = "Главный Администратор"
                admin_phone = f"+7{''.join(secrets.choice(string.digits) for _ in range(10))}"
                hashed_password = hash_password(admin_password)
                
                admin = User(
                    full_name=admin_full_name,
                    email=admin_email,
                    phone=admin_phone,
                    password=hashed_password,
                    role=UserRoleEnum.admin,
                    is_admin=True,
                    is_blocked=False
                )
                
                session.add(admin)
                await session.commit()
                await session.refresh(admin)
                
                print("\n" + "=" * 70)
                print("🎉 НОВЫЙ АДМИНИСТРАТОР СОЗДАН АВТОМАТИЧЕСКИ!")
                print("=" * 70)
                print(f"📧 Email:    {admin_email}")
                print(f"🔑 Пароль:   {admin_password}")
                print(f"👤 ФИО:      {admin_full_name}")
                print(f"📱 Телефон:  {admin_phone}")
                print(f"🆔 ID:       {admin.id}")
                print("=" * 70)
                print("⚠️  ВАЖНО: СОХРАНИТЕ ЭТИ ДАННЫЕ!")
                print("=" * 70 + "\n")
            
            await engine.dispose()
            return  # Успешно завершено
        
        except Exception as e:
            print(f"⚠️  Попытка {attempt} не удалась: {e}")
            
            if attempt < max_retries:
                print(f"   Повторная попытка через {retry_delay} секунд...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Экспоненциальная задержка
            else:
                print("❌ Не удалось инициализировать администратора после всех попыток")
                print("   Проверьте подключение к базе данных")


if __name__ == "__main__":
    asyncio.run(init_admin())
