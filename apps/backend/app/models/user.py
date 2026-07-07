from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import UserRole
from app.db.base_class import Base, NullableTextListsMixin, ShortString, TimestampMixin, UUIDPrimaryKeyMixin, enum_values

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.finance import BalanceTransaction, Payment, Subscription
    from app.models.misc import Complaint, Event, Referral, SupportTicket, VacancyView
    from app.models.organization import HRProfile, Vacancy


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int | None] = mapped_column(nullable=True, unique=True, index=True)
    vk_id: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, values_callable=enum_values),
        default=UserRole.STUDENT,
        nullable=False,
    )
    username: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    first_name: Mapped[str] = mapped_column(ShortString, nullable=False)
    last_name: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    phone: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    email: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mute_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student_profile: Mapped[StudentProfile | None] = relationship(back_populates="user", uselist=False)
    hr_profile: Mapped[HRProfile | None] = relationship(back_populates="user", uselist=False)

    created_vacancies: Mapped[list[Vacancy]] = relationship(back_populates="hr_user")
    student_applications: Mapped[list[Application]] = relationship(
        back_populates="student_user",
        foreign_keys="Application.student_user_id",
    )
    hr_applications: Mapped[list[Application]] = relationship(
        back_populates="hr_user",
        foreign_keys="Application.hr_user_id",
    )
    vacancy_views: Mapped[list[VacancyView]] = relationship(back_populates="user")
    payments: Mapped[list[Payment]] = relationship(back_populates="user")
    balance_transactions: Mapped[list[BalanceTransaction]] = relationship(back_populates="user")
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="user")
    referrals_sent: Mapped[list[Referral]] = relationship(
        back_populates="referrer_user",
        foreign_keys="Referral.referrer_user_id",
    )
    referrals_received: Mapped[list[Referral]] = relationship(
        back_populates="referred_user",
        foreign_keys="Referral.referred_user_id",
    )
    complaints_reported: Mapped[list[Complaint]] = relationship(
        back_populates="reporter_user",
        foreign_keys="Complaint.reporter_user_id",
    )
    complaints_targeted: Mapped[list[Complaint]] = relationship(
        back_populates="target_user",
        foreign_keys="Complaint.target_user_id",
    )
    support_tickets: Mapped[list[SupportTicket]] = relationship(back_populates="user")
    events: Mapped[list[Event]] = relationship(back_populates="user")


class StudentProfile(UUIDPrimaryKeyMixin, TimestampMixin, NullableTextListsMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    university: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    course: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speciality: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    experience_text: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="student_profile")
