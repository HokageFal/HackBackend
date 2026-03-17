import enum
from datetime import datetime

from sqlalchemy import Integer, TIMESTAMP, Enum, func, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.core import Base  # твой Base


class TokenTransactionType(str, enum.Enum):
    subscription = "subscription"
    purchase = "purchase"
    usage = "usage"
    refund = "refund"
    admin_adjustment = "admin_adjustment"


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    amount: Mapped[int] = mapped_column(Integer)
    # +1000 или -20

    type: Mapped[TokenTransactionType] = mapped_column(
        Enum(TokenTransactionType)
    )

    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
