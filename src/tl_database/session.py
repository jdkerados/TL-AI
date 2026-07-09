"""Engine and session factories for the TL-AI persistence layer."""

import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL_ENV_VAR = "TL_DATABASE_URL"
DEFAULT_DATABASE_URL = "postgresql+psycopg://tlai:tlai_dev_password@localhost:5432/tlai"


def get_database_url() -> str:
    """Resolve the database URL from the environment, falling back to the local dev default."""
    return os.environ.get(DATABASE_URL_ENV_VAR, DEFAULT_DATABASE_URL)


def get_engine(url: str | None = None, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL or SQLite."""
    return create_engine(url or get_database_url(), echo=echo)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory bound to the given engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)
