"""Database connection for FastAPI."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import APIConfig

# Create async engine
engine = create_async_engine(
    APIConfig.DATABASE_URL,
    echo=False,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.
    
    Yields:
        AsyncSession instance
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
