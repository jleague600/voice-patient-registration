from app.db.session import Base, engine
from app.models.patient import Patient  


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)