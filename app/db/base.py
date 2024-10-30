from sqlalchemy.ext.declarative import declarative_base

from .session import engine

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
