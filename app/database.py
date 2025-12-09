from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://usuario_api:qLOEsZzJHzqjNBEQDuwEjGXL2dGU4Aq5@dpg-d4s5b77diees73dkljd0-a.ohio-postgres.render.com/db_api_usuarios"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()
