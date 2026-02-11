"""Script to check database indexes."""
import asyncio
from sqlalchemy import text
from app.database import engine


async def check_indexes():
    """Check what indexes exist in the database."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                """
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE schemaname='public'
                ORDER BY tablename, indexname
                """
            )
        )

        print("\nDatabase Indexes:")
        print("=" * 80)
        current_table = None
        for row in result:
            table = row[1]
            index = row[0]

            if table != current_table:
                print(f"\n{table}:")
                current_table = table

            print(f"  - {index}")

        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(check_indexes())
