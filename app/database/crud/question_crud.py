from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.models.questions import Question
from app.database.models.enums import QuestionType


async def create_question(
    session: AsyncSession,
    test_id: int,
    question_text: str,
    question_type: QuestionType,
    display_order: Optional[int] = None,
    section_id: Optional[int] = None,
    is_required: bool = True,
    settings: Optional[dict] = None
) -> Question:
    question = Question(
        test_id=test_id,
        section_id=section_id,
        text=question_text,
        type=question_type,
        position=display_order or 0,
        settings_json=settings
    )
    session.add(question)
    await session.flush()
    return question


async def get_questions_by_test(
    session: AsyncSession,
    test_id: int
) -> list[Question]:
    result = await session.execute(
        select(Question)
        .where(Question.test_id == test_id)
        .order_by(Question.position)
    )
    return list(result.scalars().all())


async def get_questions_by_section(
    session: AsyncSession,
    section_id: int
) -> list[Question]:
    result = await session.execute(
        select(Question)
        .where(Question.section_id == section_id)
        .order_by(Question.position)
    )
    return list(result.scalars().all())


async def update_question(
    session: AsyncSession,
    question_id: int,
    text: Optional[str] = None,
    question_type: Optional[QuestionType] = None,
    position: Optional[int] = None,
    section_id: Optional[int] = None,
    settings_json: Optional[dict] = None
) -> Optional[Question]:
    result = await session.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalars().first()
    
    if not question:
        return None
    
    if text is not None:
        question.text = text
    if question_type is not None:
        question.type = question_type
    if position is not None:
        question.position = position
    if section_id is not None:
        question.section_id = section_id
    if settings_json is not None:
        question.settings_json = settings_json
    
    await session.flush()
    # await session.refresh(question)
    return question


async def delete_question(session: AsyncSession, question_id: int) -> bool:
    result = await session.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalars().first()
    
    if not question:
        return False
    
    await session.delete(question)
    await session.flush()
    return True



async def count_questions_by_test(session: AsyncSession, test_id: int) -> int:
    result = await session.execute(
        select(func.count(Question.id))
        .where(Question.test_id == test_id)
    )
    return result.scalar() or 0


async def get_question_by_id(session: AsyncSession, question_id: int) -> Optional[Question]:
    result = await session.execute(
        select(Question).where(Question.id == question_id)
    )
    return result.scalars().first()
