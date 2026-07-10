from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/live")
def live() -> dict:
    return {"status": "alive"}


@router.get("/ready")
def ready(session: Session = Depends(get_db_session)) -> dict:
    try:
        session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }