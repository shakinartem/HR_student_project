from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ApplicationStatus
from app.db.base_class import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values

if TYPE_CHECKING:
    from app.models.organization import Vacancy
    from app.models.user import User


class Application(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    vacancy_id: Mapped[object] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    student_user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hr_user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False, values_callable=enum_values),
        default=ApplicationStatus.SENT,
        nullable=False,
    )
    student_comment: Mapped[str | None] = mapped_column(String, nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    vacancy: Mapped[Vacancy] = relationship(back_populates="applications")
    student_user: Mapped[User] = relationship(
        back_populates="student_applications",
        foreign_keys=[student_user_id],
    )
    hr_user: Mapped[User] = relationship(
        back_populates="hr_applications",
        foreign_keys=[hr_user_id],
    )
