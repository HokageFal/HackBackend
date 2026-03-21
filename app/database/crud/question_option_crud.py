from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.models.question_options import QuestionOption


async def create_option(
    session: AsyncSession,
    question_id: int,
    text: str,
    position: int
) -> QuestionOption:
    option = QuestionOption(
        question_id=question_id,
        text=text,
        position=position
    )
    session.add(option)
    await session.commit()
    await session.refresh(option)
    return option


async def get_options_by_question(
    session: AsyncSession,
    question_id: int
) -> list[QuestionOption]:
    result = await session.execute(
        select(QuestionOption)
        .where(QuestionOption.question_id == question_id)
        .order_by(QuestionOption.position)
    )
    return list(result.scalars().all())


async def update_option(
    session: AsyncSession,
    option_id: int,
    text: Optional[str] = None,
    position: Optional[int] = None
) -> Optional[QuestionOption]:
    result = await session.execute(
        select(QuestionOption).where(QuestionOption.id == option_id)
    )
    option = result.scalars().first()
    
    if not option:
        return None
    
    if text is not None:
        option.text = text
    if position is not None:
        option.position = position
    
    await session.commit()
    await session.refresh(option)
    return option


async def delete_option(session: AsyncSession, option_id: int) -> bool:
    result = await session.execute(
        select(QuestionOption).where(QuestionOption.id == option_id)
    )
    option = result.scalars().first()
    
    if not option:
        return False
    
    await session.delete(option)
    await session.commit()
    return True
