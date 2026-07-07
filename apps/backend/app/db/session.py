from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def get_engine(database_url: str | None = None, *, echo: bool | None = None) -> Engine:
    settings = get_settings()
    url = database_url or settings.database_url
    engine_echo = False if echo is None else echo
    return create_engine(url, echo=engine_echo, future=True)

def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    engine = get_engine(database_url=database_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Session:
    return get_session_factory()()
