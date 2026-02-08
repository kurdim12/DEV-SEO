import asyncio
import asyncpg

async def test_connection():
    # Test different username formats
    ip = '44.216.29.125'  # First pooler IP

    username_formats = [
        'postgres',
        'postgres.ycbismsbncrdphexcfyv',
        'ycbismsbncrdphexcfyv',
        'postgres:ycbismsbncrdphexcfyv',
    ]

    for username in username_formats:
        print(f"Testing username: {username}")
        try:
            conn = await asyncpg.connect(
                host=ip,
                port=6543,
                user=username,
                password='WMMgOz0QXbZoTpoc',
                database='postgres',
                timeout=10
            )
            print(f"SUCCESS with username: {username}")
            await conn.close()
            return username
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {str(e)[:100]}")

    print("\nAll username formats failed")
    return None

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    if result:
        print(f"\nCorrect username format: {result}")
