from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import HRStatus, VacancyStatus
from app.db.base_class import Base, ShortString, TimestampMixin, UUIDPrimaryKeyMixin, enum_values

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.misc import VacancyView
    from app.models.user import User


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(ShortString, nullable=False, unique=True)
    inn: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    contact_telegram: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    status: Mapped[str] = mapped_column(ShortString, default="active", nullable=False)

    hr_profiles: Mapped[list[HRProfile]] = relationship(back_populates="company")
    vacancies: Mapped[list[Vacancy]] = relationship(back_populates="company")


class HRProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "hr_profiles"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_id: Mapped[object] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    verified_status: Mapped[HRStatus] = mapped_column(
        Enum(HRStatus, native_enum=False, values_callable=enum_values),
        default=HRStatus.PENDING,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="hr_profile")
    company: Mapped[Company] = relationship(back_populates="hr_profiles")


class Vacancy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "vacancies"

    company_id: Mapped[object] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    hr_user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(ShortString, nullable=False)
    category: Mapped[str] = mapped_column(ShortString, nullable=False)
    job_type: Mapped[str] = mapped_column(ShortString, nullable=False)
    schedule: Mapped[str] = mapped_column(ShortString, nullable=False)
    salary_text: Mapped[str] = mapped_column(ShortString, nullable=False)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    district: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    address: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    format: Mapped[str | None] = mapped_column("format", ShortString, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(String, nullable=True)
    requirements: Mapped[str | None] = mapped_column(String, nullable=True)
    conditions: Mapped[str | None] = mapped_column(String, nullable=True)
    experience_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    status: Mapped[VacancyStatus] = mapped_column(
        Enum(VacancyStatus, native_enum=False, values_callable=enum_values),
        default=VacancyStatus.DRAFT,
        nullable=False,
    )
    moderation_status: Mapped[str] = mapped_column(ShortString, default="manual_review", nullable=False)
    is_promoted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    promotion_type: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    promotion_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped[Company] = relationship(back_populates="vacancies")
    hr_user: Mapped[User] = relationship(back_populates="created_vacancies")
    applications: Mapped[list[Application]] = relationship(back_populates="vacancy")
    views: Mapped[list[VacancyView]] = relationship(back_populates="vacancy")
