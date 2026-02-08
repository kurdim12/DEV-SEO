import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server (trust auth enabled temporarily)
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    user="postgres",
    password=""
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

try:
    # Create user
    cursor.execute("CREATE USER devseo WITH PASSWORD 'devseo_dev_pass';")
    print("✓ User 'devseo' created successfully")
except Exception as e:
    print(f"User creation: {e}")

try:
    # Create database
    cursor.execute("CREATE DATABASE devseo OWNER devseo;")
    print("✓ Database 'devseo' created successfully")
except Exception as e:
    print(f"Database creation: {e}")

try:
    # Grant privileges
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE devseo TO devseo;")
    print("✓ Privileges granted successfully")
except Exception as e:
    print(f"Grant privileges: {e}")

cursor.close()
conn.close()
print("\n✅ Database setup complete!")
