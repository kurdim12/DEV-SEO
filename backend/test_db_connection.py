import asyncio
import asyncpg

async def test_connection():
    # Test 1: Direct connection
    print("Testing direct connection...")
    try:
        conn = await asyncpg.connect(
            host='db.ycbismsbncrdphexcfyv.supabase.co',
            port=5432,
            user='postgres',
            password='WMMgOz0QXbZoTpoc',
            database='postgres',
            timeout=30
        )
        print("✓ Direct connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"✗ Direct connection failed: {type(e).__name__}: {e}")

    # Test 2: Pooler connection with session mode
    print("\nTesting pooler connection (session mode)...")
    try:
        conn = await asyncpg.connect(
            host='aws-0-us-east-1.pooler.supabase.com',
            port=6543,
            user='postgres.ycbismsbncrdphexcfyv',
            password='WMMgOz0QXbZoTpoc',
            database='postgres',
            timeout=30
        )
        print("✓ Pooler connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"✗ Pooler connection failed: {type(e).__name__}: {e}")

    # Test 3: Pooler with plain username
    print("\nTesting pooler with plain postgres username...")
    try:
        conn = await asyncpg.connect(
            host='aws-0-us-east-1.pooler.supabase.com',
            port=6543,
            user='postgres',
            password='WMMgOz0QXbZoTpoc',
            database='postgres',
            timeout=30
        )
        print("✓ Pooler (plain) connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"✗ Pooler (plain) connection failed: {type(e).__name__}: {e}")

    return False

if __name__ == "__main__":
    asyncio.run(test_connection())
