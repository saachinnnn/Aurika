import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# Database Configuration
DB_USER = os.getenv("POSTGRES_USER", "aurika_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password123")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "aurika_db")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create Async Engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base Class for Models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI/Dependency Injection
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
