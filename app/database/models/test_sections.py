from sqlalchemy import BigInteger, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base


class TestSection(Base):
    __tablename__ = "test_sections"
    __table_args__ = (
        UniqueConstraint("test_id", "position", name="uq_test_section_position"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    test: Mapped["Test"] = relationship("Test", back_populates="sections")
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="section"
    )
