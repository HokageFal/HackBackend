from sqlalchemy import BigInteger, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database.core import Base
from app.database.models.enums import ReportAudience


class ReportTemplate(Base):
    __tablename__ = "report_templates"
    __table_args__ = (
        UniqueConstraint("test_id", "audience", name="uq_report_template_audience"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False
    )
    audience: Mapped[ReportAudience] = mapped_column(Enum(ReportAudience), nullable=False)
    template_definition: Mapped[dict] = mapped_column(JSONB, nullable=False)

    test: Mapped["Test"] = relationship("Test", back_populates="report_templates")
