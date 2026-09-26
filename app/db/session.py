"""
Database engine and session management.

Creates a single async SQLAlchemy engine (reused across requests) and
exposes a session factory. Routes never talk to the engine directly --
they depend on `get_session()` via FastAPI's dependency injection
(see app/api/deps.py).

NOTE on Supabase's pgbouncer transaction-mode pooler: it does not
support prepared statements, since a "prepared statement" is normally
tied to one persistent connection, but pgbouncer in transaction mode
hands out a different underlying connection for every transaction.
asyncpg's default behavior of preparing+caching statements breaks
under this setup with DuplicatePreparedStatementError. Fixing this
requires BOTH:
  1. Disabling asyncpg's own statement cache (statement_cache_size=0)
  2. Giving every prepared statement a unique/blank name via
     prepared_statement_name_func, so SQLAlchemy's internal caching
     layer doesn't collide either
  3. Using NullPool so SQLAlchemy doesn't attempt to reuse a raw
     connection across requests -- pgbouncer is already doing pooling
     underneath us, so a second pooling layer on top is redundant
     and is what's causing the collision.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings


class Base(DeclarativeBase):
    """Base class all ORM models (e.g. Patient) inherit from."""
    pass


def _unique_statement_name(*args, **kwargs) -> str:
    """Gives every prepared statement a unique name so asyncpg never
    tries to reuse/collide a statement name across pooled connections."""
    return f"__asyncpg_{uuid.uuid4().hex}__"


engine = create_async_engine(
    settings.database_url,
    echo=(settings.environment == "development"),
    poolclass=NullPool,  # let pgbouncer handle pooling; don't pool on top of it
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": _unique_statement_name,
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """FastAPI dependency: yields a DB session, closes it after the request."""
    async with AsyncSessionLocal() as session:
        yield session