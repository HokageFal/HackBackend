from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.database.models.user_answers import UserAnswer


async def create_user_answer(
    session: AsyncSession,
    attempt_id: int,
    question_id: int,
    text_answer: Optional[str] = None,
    boolean_answer: Optional[bool] = None,
    number_answer: Optional[Decimal] = None,
    datetime_answer: Optional[datetime] = None
) -> UserAnswer:
    answer = UserAnswer(
        attempt_id=attempt_id,
        question_id=question_id,
        text_answer=text_answer,
        boolean_answer=boolean_answer,
        number_answer=number_answer,
        datetime_answer=datetime_answer
    )
    session.add(answer)
    await session.commit()
    await session.refresh(answer)
    return answer


async def get_answers_by_attempt(
    session: AsyncSession,
    attempt_id: int
) -> list[UserAnswer]:
    result = await session.execute(
        select(UserAnswer)
        .where(UserAnswer.attempt_id == attempt_id)
    )
    return list(result.scalars().all())


async def get_answer_by_question(
    session: AsyncSession,
    attempt_id: int,
    question_id: int
) -> Optional[UserAnswer]:
    result = await session.execute(
        select(UserAnswer).where(
            UserAnswer.attempt_id == attempt_id,
            UserAnswer.question_id == question_id
        )
    )
    return result.scalars().first()
