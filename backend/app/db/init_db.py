import asyncio
import logging
from app.db.database import engine, setup_database
from app.db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_models():
    """Drops all tables and recreates them, ensuring the vector extension is present."""
    logger.info("Initializing database setup...")
    
    # 1. Setup Database Extensions
    logger.info("Ensuring pgvector extension exists...")
    await setup_database()

    # 2. Recreate Tables
    async with engine.begin() as conn:
        logger.info("Dropping all existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Creating all tables from models...")
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialization completed successfully!")

if __name__ == "__main__":
    asyncio.run(init_models())
