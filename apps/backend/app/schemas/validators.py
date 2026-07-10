from __future__ import annotations

import re

from pydantic import field_validator


def validate_phone(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"[^\d+]", "", value)
    if not re.match(r"^\+?\d{7,15}$", cleaned):
        raise ValueError("Phone must be in international format (e.g. +79991234567)")
    return cleaned


def validate_email(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", normalized):
        raise ValueError("Invalid email format")
    return normalized