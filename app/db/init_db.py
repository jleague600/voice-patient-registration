from app.db.session import Base, engine
from app.models.patient import Patient


# This creates the tables when the app starts.
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)