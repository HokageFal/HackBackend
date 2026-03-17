
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.users import User
from app.database.models.token_ledger import TokenTransaction, TokenTransactionType


async def get_user_for_update(session: AsyncSession, user_id: int) -> User | None:
    return await session.scalar(
        select(User)
        .where(User.id == user_id)
        .with_for_update()
    )


def add_token_balance(user: User, amount: int) -> None:
    user.token_balance += amount


def deduct_token_balance(user: User, amount: int) -> None:
    user.token_balance -= amount


def create_token_transaction(
    session: AsyncSession,
    user_id: int,
    amount: int,
    transaction_type: TokenTransactionType,
    description: str | None = None
) -> TokenTransaction:
    return TokenTransaction(
        user_id=user_id,
        amount=amount,
        type=transaction_type,
        description=description
    )


async def get_user_transactions(
    session: AsyncSession,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> list[TokenTransaction]:
    result = await session.execute(
        select(TokenTransaction)
        .where(TokenTransaction.user_id == user_id)
        .order_by(TokenTransaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
