from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_answer_options import UserAnswerOption


async def create_answer_option(
    session: AsyncSession,
    user_answer_id: int,
    option_id: int
) -> UserAnswerOption:
    answer_option = UserAnswerOption(
        user_answer_id=user_answer_id,
        option_id=option_id
    )
    session.add(answer_option)
    await session.flush()
    # await session.refresh(answer_option)
    return answer_option


async def get_selected_options(
    session: AsyncSession,
    user_answer_id: int
) -> list[UserAnswerOption]:
    result = await session.execute(
        select(UserAnswerOption)
        .where(UserAnswerOption.user_answer_id == user_answer_id)
    )
    return list(result.scalars().all())




async def get_options_by_answer(
    session: AsyncSession,
    user_answer_id: int
) -> list[UserAnswerOption]:
    result = await session.execute(
        select(UserAnswerOption)
        .where(UserAnswerOption.user_answer_id == user_answer_id)
    )
    return list(result.scalars().all())
