from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentStatus, SubscriptionStatus
from app.db.base_class import Base, ShortString, TimestampMixin, UUIDPrimaryKeyMixin, enum_values, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class Payment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "payments"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(ShortString, default="RUB", nullable=False)
    provider: Mapped[str] = mapped_column(ShortString, nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(ShortString, nullable=True, unique=True)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, values_callable=enum_values),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(ShortString, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    entity_id: Mapped[str | None] = mapped_column(ShortString, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="payments")
    balance_transactions: Mapped[list[BalanceTransaction]] = relationship(back_populates="payment")


class BalanceTransaction(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "balance_transactions"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(ShortString, nullable=False)
    reason: Mapped[str] = mapped_column(ShortString, nullable=False)
    payment_id: Mapped[object | None] = mapped_column(ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="balance_transactions")
    payment: Mapped[Payment | None] = relationship(back_populates="balance_transactions")


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[object] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, native_enum=False, values_callable=enum_values),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="subscriptions")


class Tariff(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tariffs"

    code: Mapped[str] = mapped_column(ShortString, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(ShortString, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
