from sqlalchemy import BigInteger, String, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional

from app.database.core import Base
from app.database.models.enums import QuestionType


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("test_id", "position", name="uq_question_position"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False
    )
    section_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("test_sections.id", ondelete="SET NULL"),
        nullable=True
    )
    text: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    settings_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    test: Mapped["Test"] = relationship("Test", back_populates="questions")
    section: Mapped[Optional["TestSection"]] = relationship("TestSection", back_populates="questions")
    options: Mapped[list["QuestionOption"]] = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan"
    )
    user_answers: Mapped[list["UserAnswer"]] = relationship(
        "UserAnswer",
        back_populates="question",
        cascade="all, delete-orphan"
    )
