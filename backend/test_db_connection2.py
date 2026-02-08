import asyncio
import asyncpg

async def test_connection():
    # Test with IPv4 pooler IPs directly
    pooler_ips = ['44.216.29.125', '44.208.221.186', '52.45.94.125']

    for ip in pooler_ips:
        print(f"Testing pooler IP {ip}:6543...")
        try:
            conn = await asyncpg.connect(
                host=ip,
                port=6543,
                user='postgres.ycbismsbncrdphexcfyv',
                password='WMMgOz0QXbZoTpoc',
                database='postgres',
                server_settings={'search_path': 'public'},
                timeout=15
            )
            print(f"SUCCESS! Connected via pooler IP {ip}")
            version = await conn.fetchval('SELECT version()')
            print(f"PostgreSQL version: {version}")
            await conn.close()
            return ip
        except Exception as e:
            print(f"FAILED on {ip}: {type(e).__name__}: {e}")
            continue

    print("\nAll connection attempts failed")
    return None

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    if result:
        print(f"\nUse this IP in your connection string: {result}")
