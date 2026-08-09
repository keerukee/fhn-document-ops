from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Note: for async, we should use postgresql+asyncpg:// but for local dev sqlite+aiosqlite:// works
engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
