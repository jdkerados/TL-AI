"""Declarative base and shared column types for the TL-AI persistence layer."""

from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeEngine

EMBEDDING_DIMENSIONS = 1024

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def json_type() -> TypeEngine[Any]:
    """JSON column type: JSONB on PostgreSQL, JSON on SQLite."""
    return JSON().with_variant(JSONB(), "postgresql")


def embedding_type() -> TypeEngine[Any]:
    """Embedding vector type: pgvector on PostgreSQL, JSON fallback on SQLite."""
    return Vector(EMBEDDING_DIMENSIONS).with_variant(JSON(), "sqlite")


class Base(DeclarativeBase):
    """Declarative base for all TL-AI ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
