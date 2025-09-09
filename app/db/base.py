from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    """Root declarative base class for all SQLAlchemy models."""

    pass


# Polymorphic JSON type: uses Postgres JSONB in production, standard JSON for SQLite
JSONType = JSON().with_variant(JSONB, "postgresql")
