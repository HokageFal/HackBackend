"""
Скрипт для создания тестовых завершенных попыток прохождения тестов.

Использование:
    python create_test_attempts.py

Что делает:
    1. Подключается к БД
    2. Находит существующие тесты
    3. Создает несколько завершенных попыток с ответами
"""

import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from app.database.crud.test_crud import get_tests_by_psychologist
from app.database.crud.test_profile_field_crud import get_profile_fields_by_test
from app.database.crud.question_crud import get_questions_by_test
from app.database.crud.question_option_crud import get_options_by_question
from app.database.crud.test_attempt_crud import create_attempt, submit_attempt
from app.database.crud.test_attempt_profile_value_crud import create_profile_value
from app.database.crud.user_answer_crud import create_user_answer
from app.database.crud.user_answer_option_crud import create_answer_option
from app.database.crud.test_crud import increment_attempts_count
from app.database.models.enums import QuestionType

load_dotenv()

# Настройка подключения к БД
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL не найден в .env файле")
    sys.exit(1)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Тестовые данные клиентов
TEST_CLIENTS = [
    "Иванов Иван Иванович",
    "Петрова Мария Сергеевна",
    "Сидоров Алексей Петрович",
    "Козлова Елена Владимировна",
    "Морозов Дмитрий Александрович",
    "Новикова Анна Игоревна",
    "Волков Сергей Николаевич",
    "Соколова Ольга Андреевна",
]


async def create_test_attempt_with_answers(
    session: AsyncSession,
    test_id: int,
    client_name: str,
    days_ago: int = 0
):
    """Создает одну завершенную попытку с ответами"""
    
    print(f"\n📝 Создаю попытку для клиента: {client_name}")
    
    # Получаем структуру теста
    profile_fields = await get_profile_fields_by_test(session, test_id)
    questions = await get_questions_by_test(session, test_id)
    
    if not questions:
        print(f"⚠️  Тест {test_id} не имеет вопросов, пропускаю")
        return None
    
    # Создаем попытку
    started_at = datetime.utcnow() - timedelta(days=days_ago, hours=1)
    attempt = await create_attempt(session, test_id, client_name)
    attempt.started_at = started_at
    await session.flush()
    
    print(f"✅ Попытка создана (ID: {attempt.id})")
    
    # Заполняем поля профиля
    for i, field in enumerate(profile_fields):
        if field.type.value == "text":
            value = f"Значение {i+1}"
            await create_profile_value(session, attempt.id, field.id, text_value=value)
        elif field.type.value == "number":
            value = Decimal(str(20 + i * 5))
            await create_profile_value(session, attempt.id, field.id, number_value=value)
    
    print(f"✅ Заполнено {len(profile_fields)} полей профиля")
    
    # Отвечаем на вопросы
    answered = 0
    for question in questions:
        answer = None
        
        if question.type == QuestionType.text:
            answer = await create_user_answer(
                session, attempt.id, question.id,
                text_answer=f"Ответ на вопрос {question.id}"
            )
        
        elif question.type == QuestionType.textarea:
            answer = await create_user_answer(
                session, attempt.id, question.id,
                text_answer=f"Развернутый ответ на вопрос {question.id}. Это более длинный текст с деталями."
            )
        
        elif question.type == QuestionType.boolean:
            answer = await create_user_answer(
                session, attempt.id, question.id,
                boolean_answer=True if question.id % 2 == 0 else False
            )
        
        elif question.type == QuestionType.number:
            answer = await create_user_answer(
                session, attempt.id, question.id,
                number_answer=Decimal(str(42 + question.id))
            )
        
        elif question.type == QuestionType.slider:
            settings = question.settings_json or {}
            min_val = settings.get("min", 0)
            max_val = settings.get("max", 100)
            value = (min_val + max_val) // 2
            answer = await create_user_answer(
                session, attempt.id, question.id,
                number_answer=Decimal(str(value))
            )
        
        elif question.type == QuestionType.rating_scale:
            settings = question.settings_json or {}
            max_val = settings.get("max", 10)
            value = max_val - 2
            answer = await create_user_answer(
                session, attempt.id, question.id,
                number_answer=Decimal(str(value))
            )
        
        elif question.type == QuestionType.datetime:
            answer = await create_user_answer(
                session, attempt.id, question.id,
                datetime_answer=datetime.utcnow() - timedelta(days=365*25)
            )
        
        elif question.type in [QuestionType.single_choice, QuestionType.multiple_choice]:
            options = await get_options_by_question(session, question.id)
            if options:
                answer = await create_user_answer(
                    session, attempt.id, question.id
                )
                
                if question.type == QuestionType.single_choice:
                    # Выбираем первую опцию
                    await create_answer_option(session, answer.id, options[0].id)
                else:
                    # Выбираем первые 2 опции для multiple choice
                    for opt in options[:2]:
                        await create_answer_option(session, answer.id, opt.id)
        
        if answer:
            answered += 1
    
    print(f"✅ Отвечено на {answered} вопросов")
    
    # Завершаем попытку
    submitted_at = started_at + timedelta(minutes=30 + days_ago * 5)
    submitted_attempt = await submit_attempt(session, attempt.id)
    submitted_attempt.submitted_at = submitted_at
    await session.flush()
    
    # Инкрементируем счетчик
    await increment_attempts_count(session, test_id)
    
    print(f"✅ Попытка завершена")
    
    return attempt


async def main():
    """Основная функция"""
    
    print("=" * 60)
    print("🚀 Скрипт создания тестовых попыток прохождения")
    print("=" * 60)
    
    async with async_session() as session:
        try:
            # Находим первого психолога (обычно ID=1 если создавали через init_admin)
            psychologist_id = 1
            
            print(f"\n🔍 Ищу тесты психолога ID={psychologist_id}...")
            
            tests, total = await get_tests_by_psychologist(session, psychologist_id, skip=0, limit=10)
            
            if not tests:
                print(f"\n❌ У психолога ID={psychologist_id} нет тестов!")
                print("\n💡 Сначала создайте тест через API:")
                print("   POST /tests")
                return
            
            print(f"\n✅ Найдено тестов: {len(tests)}")
            
            # Для каждого теста создаем несколько попыток
            for test in tests:
                print(f"\n{'='*60}")
                print(f"📋 Тест: {test.title} (ID: {test.id})")
                print(f"{'='*60}")
                
                # Создаем 3-5 попыток для каждого теста
                num_attempts = min(5, len(TEST_CLIENTS))
                
                for i in range(num_attempts):
                    client_name = TEST_CLIENTS[i]
                    days_ago = i * 2  # Разные даты
                    
                    await create_test_attempt_with_answers(
                        session,
                        test.id,
                        client_name,
                        days_ago
                    )
            
            # Сохраняем все изменения
            await session.commit()
            
            print("\n" + "=" * 60)
            print("✅ Все тестовые попытки успешно созданы!")
            print("=" * 60)
            print("\n📊 Теперь можно проверить через API:")
            print(f"   GET /tests/{{test_id}}/attempts")
            print(f"   GET /attempts/{{attempt_id}}")
            print(f"   GET /attempts/{{attempt_id}}/report/client")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    print("\n⚙️  Запуск скрипта...\n")
    asyncio.run(main())
