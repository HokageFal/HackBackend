from sqlalchemy import BigInteger, String, Boolean, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.database.core import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_user_answer"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("test_attempts.id", ondelete="CASCADE"),
        nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )
    text_answer: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    boolean_answer: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    number_answer: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)
    datetime_answer: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    attempt: Mapped["TestAttempt"] = relationship("TestAttempt", back_populates="user_answers")
    question: Mapped["Question"] = relationship("Question", back_populates="user_answers")
    selected_options: Mapped[list["UserAnswerOption"]] = relationship(
        "UserAnswerOption",
        back_populates="user_answer",
        cascade="all, delete-orphan"
    )
