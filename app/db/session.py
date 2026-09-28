import uuid
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings


# Base class for all SQLAlchemy models.
class Base(DeclarativeBase):
    """Base class all ORM models (e.g. Patient) inherit from."""
    pass


# This makes each SQL statement name unique. Helps avoid issues with asyncpg.
def _unique_statement_name(*args, **kwargs) -> str:
    """Gives every prepared statement a unique name so asyncpg never
    tries to reuse/collide a statement name across pooled connections."""
    return f"__asyncpg_{uuid.uuid4().hex}__"


# Create the async database engine.
engine = create_async_engine(
    settings.database_url,
    echo=(settings.environment == "development"),
    poolclass=NullPool,  # dont do extra pooling because Supabase pooler already handles it
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": _unique_statement_name,
    },
)

# This is the session factory used by FastAPI routes.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# This function gives each request a DB session and then closes it after use.
async def get_session() -> AsyncSession:
    """FastAPI dependency: yields a DB session, closes it after the request."""
    async with AsyncSessionLocal() as session:
        yield session