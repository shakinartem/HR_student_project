from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, ShortString, UUIDPrimaryKeyMixin, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class RoleAudit(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "role_audit"

    changed_by_user_id: Mapped[object] = mapped_column(
        "changed_by_user_id",
        type_=ShortString,
        nullable=False,
    )
    target_user_id: Mapped[object] = mapped_column(ShortString, nullable=False)
    old_role: Mapped[str | None] = mapped_column(String, nullable=True)
    new_role: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)