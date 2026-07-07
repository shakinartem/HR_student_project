from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ComplaintStatus, ModerationResult, SupportTicketStatus
from app.db.base_class import Base, ShortString, TimestampMixin, UUIDPrimaryKeyMixin, enum_values, utc_now

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.organization import Vacancy
    from app.models.user import User


class VacancyView(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "vacancy_views"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vacancy_id: Mapped[object] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="vacancy_views")
    vacancy: Mapped[Vacancy] = relationship(back_populates="views")


class GuestVacancyView(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "guest_vacancy_views"

    guest_id: Mapped[str] = mapped_column(ShortString, nullable=False, index=True)
    vacancy_id: Mapped[object] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)

    vacancy: Mapped[Vacancy] = relationship()


class Referral(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "referrals"

    referrer_user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    referred_user_id: Mapped[object | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    code: Mapped[str] = mapped_column(ShortString, nullable=False, unique=True)
    type: Mapped[str] = mapped_column(ShortString, nullable=False)
    status: Mapped[str] = mapped_column(ShortString, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)

    referrer_user: Mapped[User] = relationship(
        back_populates="referrals_sent",
        foreign_keys=[referrer_user_id],
    )
    referred_user: Mapped[User | None] = relationship(
        back_populates="referrals_received",
        foreign_keys=[referred_user_id],
    )


class Complaint(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "complaints"

    reporter_user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vacancy_id: Mapped[object | None] = mapped_column(ForeignKey("vacancies.id", ondelete="SET NULL"), nullable=True)
    application_id: Mapped[object | None] = mapped_column(ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus, native_enum=False, values_callable=enum_values),
        default=ComplaintStatus.OPEN,
        nullable=False,
    )
    admin_comment: Mapped[str | None] = mapped_column(String, nullable=True)

    reporter_user: Mapped[User] = relationship(
        back_populates="complaints_reported",
        foreign_keys=[reporter_user_id],
    )
    target_user: Mapped[User] = relationship(
        back_populates="complaints_targeted",
        foreign_keys=[target_user_id],
    )
    vacancy: Mapped[Vacancy | None] = relationship()
    application: Mapped[Application | None] = relationship()


class SupportTicket(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "support_tickets"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(ShortString, nullable=False)
    subject: Mapped[str] = mapped_column(ShortString, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[SupportTicketStatus] = mapped_column(
        Enum(SupportTicketStatus, native_enum=False, values_callable=enum_values),
        default=SupportTicketStatus.OPEN,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="support_tickets")


class ModerationLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "moderation_logs"

    entity_type: Mapped[str] = mapped_column(ShortString, nullable=False)
    entity_id: Mapped[str] = mapped_column(ShortString, nullable=False)
    result: Mapped[ModerationResult] = mapped_column(
        Enum(ModerationResult, native_enum=False, values_callable=enum_values),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class Event(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "events"

    user_id: Mapped[object | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_name: Mapped[str] = mapped_column(ShortString, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    entity_id: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)

    user: Mapped[User | None] = relationship(back_populates="events")
