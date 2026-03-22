from sqlalchemy import BigInteger, String, Date, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from app.database.core import Base


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    psychologist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    public_link_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    access_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    client_can_view_report: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attempts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    psychologist: Mapped["User"] = relationship("User", back_populates="tests")
    profile_fields: Mapped[list["TestProfileField"]] = relationship(
        "TestProfileField",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    sections: Mapped[list["TestSection"]] = relationship(
        "TestSection",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    metrics: Mapped[list["TestMetric"]] = relationship(
        "TestMetric",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    report_templates: Mapped[list["ReportTemplate"]] = relationship(
        "ReportTemplate",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    attempts: Mapped[list["TestAttempt"]] = relationship(
        "TestAttempt",
        back_populates="test",
        cascade="all, delete-orphan"
    )
