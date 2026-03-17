from datetime import datetime

from sqlalchemy import TIMESTAMP, func, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.core import Base  # твой Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("subscription_plans.id")
    )

    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)  # <--- автопродление
