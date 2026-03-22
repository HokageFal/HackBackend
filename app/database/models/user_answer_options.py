from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base


class UserAnswerOption(Base):
    __tablename__ = "user_answer_options"
    __table_args__ = (
        UniqueConstraint("user_answer_id", "option_id", name="uq_user_answer_option"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_answer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_answers.id", ondelete="CASCADE"),
        nullable=False
    )
    option_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("question_options.id", ondelete="CASCADE"),
        nullable=False
    )

    user_answer: Mapped["UserAnswer"] = relationship("UserAnswer", back_populates="selected_options")
    option: Mapped["QuestionOption"] = relationship("QuestionOption", back_populates="user_answer_options")
