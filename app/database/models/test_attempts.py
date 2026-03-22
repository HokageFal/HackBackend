from sqlalchemy import BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from app.database.core import Base


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False
    )
    client_name: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    test: Mapped["Test"] = relationship("Test", back_populates="attempts")
    profile_values: Mapped[list["TestAttemptProfileValue"]] = relationship(
        "TestAttemptProfileValue",
        back_populates="attempt",
        cascade="all, delete-orphan"
    )
    user_answers: Mapped[list["UserAnswer"]] = relationship(
        "UserAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan"
    )
