"""
Script to drop and recreate all database tables with correct types for PostgreSQL.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import AsyncSessionLocal, engine
from app.models.user import User
from app.models.website import Website
from app.models.crawl_job import CrawlJob
from app.models.page_result import PageResult


async def recreate_tables():
    """Drop all tables and recreate them with correct PostgreSQL types."""
    print("Dropping all tables...")

    async with engine.begin() as conn:
        # Drop tables in correct order (reverse of dependencies)
        await conn.execute(text("DROP TABLE IF EXISTS page_results CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS crawl_jobs CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS websites CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

    print("Creating tables with correct types...")

    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Website.metadata.create_all)
        await conn.run_sync(CrawlJob.metadata.create_all)
        await conn.run_sync(PageResult.metadata.create_all)

    print("✓ Tables recreated successfully with PostgreSQL UUID types!")


if __name__ == "__main__":
    asyncio.run(recreate_tables())
