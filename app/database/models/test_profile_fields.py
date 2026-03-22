from sqlalchemy import BigInteger, String, Boolean, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base
from app.database.models.enums import ProfileFieldType


class TestProfileField(Base):
    __tablename__ = "test_profile_fields"
    __table_args__ = (
        UniqueConstraint("test_id", "position", name="uq_test_profile_field_position"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False
    )
    label: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[ProfileFieldType] = mapped_column(Enum(ProfileFieldType), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    test: Mapped["Test"] = relationship("Test", back_populates="profile_fields")
    profile_values: Mapped[list["TestAttemptProfileValue"]] = relationship(
        "TestAttemptProfileValue",
        back_populates="profile_field",
        cascade="all, delete-orphan"
    )
