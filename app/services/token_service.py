from sqlalchemy.ext.asyncio import AsyncSession
from app.database.crud import token_crud
from app.database.models.token_ledger import TokenTransactionType


class InsufficientTokensError(Exception):
    def __init__(self, available: int, required: int):
        self.available = available
        self.required = required
        self.message = f"Недостаточно токенов. Доступно: {available}, требуется: {required}"
        super().__init__(self.message)


class UserNotFoundError(Exception):
    pass


async def credit_tokens(
    session: AsyncSession,
    user_id: int,
    amount: int,
    transaction_type: TokenTransactionType,
    description: str | None = None
) -> dict:
    user = await token_crud.get_user_for_update(session, user_id)
    
    if not user:
        raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")

    token_crud.add_token_balance(user, amount)

    transaction = token_crud.create_token_transaction(
        session=session,
        user_id=user_id,
        amount=amount,
        transaction_type=transaction_type,
        description=description
    )
    
    return {
        "new_balance": user.token_balance,
        "transaction_id": transaction.id
    }



async def debit_tokens(
    session: AsyncSession,
    user_id: int,
    amount: int,
    transaction_type: TokenTransactionType,
    description: str | None = None
) -> dict:
    # Получаем пользователя с блокировкой (защита от race condition)
    user = await token_crud.get_user_for_update(session, user_id)
    
    if not user:
        raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")
    
    # Проверяем достаточно ли токенов
    if user.token_balance < amount:
        raise InsufficientTokensError(
            available=user.token_balance,
            required=amount
        )
    
    # Списываем токены
    token_crud.deduct_token_balance(user, amount)
    
    # Создаем транзакцию (отрицательное значение)
    transaction = token_crud.create_token_transaction(
        session=session,
        user_id=user_id,
        amount=-amount,  # Отрицательное для списания
        transaction_type=transaction_type,
        description=description
    )
    
    return {
        "new_balance": user.token_balance,
        "transaction_id": transaction.id
    }
