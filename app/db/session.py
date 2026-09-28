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