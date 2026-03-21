from sqlalchemy import BigInteger, String, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import Optional
from decimal import Decimal

from app.database.core import Base


class TestAttemptProfileValue(Base):
    __tablename__ = "test_attempt_profile_values"
    __table_args__ = (
        UniqueConstraint("attempt_id", "profile_field_id", name="uq_attempt_profile_value"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("test_attempts.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_field_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("test_profile_fields.id", ondelete="CASCADE"),
        nullable=False
    )
    text_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    number_value: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)
    date_value: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    attempt: Mapped["TestAttempt"] = relationship("TestAttempt", back_populates="profile_values")
    profile_field: Mapped["TestProfileField"] = relationship("TestProfileField", back_populates="profile_values")
