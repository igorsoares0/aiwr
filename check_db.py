#!/usr/bin/env python
"""
Database Connection Diagnostic Script
Run this to check database connectivity and configuration
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_database_connection():
    """Check if database connection is working"""
    print("=" * 60)
    print("DATABASE CONNECTION DIAGNOSTIC")
    print("=" * 60)

    # Get DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL in your .env file or environment")
        return False

    print(f"\n📊 Database URL (first 50 chars): {database_url[:50]}...")

    # Check if it needs postgres:// -> postgresql:// fix
    if database_url.startswith('postgres://'):
        print("⚠️ Warning: DATABASE_URL uses 'postgres://' (old format)")
        print("   Converting to 'postgresql://' for SQLAlchemy compatibility")
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"   New URL (first 50 chars): {database_url[:50]}...")

    # Parse the URL to show details
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        print(f"\n🔍 Connection Details:")
        print(f"   Protocol: {parsed.scheme}")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port or 5432}")
        print(f"   Database: {parsed.path.lstrip('/')}")
        print(f"   Username: {parsed.username}")
        print(f"   Password: {'***' if parsed.password else 'None'}")
    except Exception as e:
        print(f"⚠️ Could not parse URL: {e}")

    # Try to connect using psycopg2 directly
    print("\n🔌 Testing direct psycopg2 connection...")
    try:
        import psycopg2
        from urllib.parse import urlparse

        parsed = urlparse(database_url)

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            connect_timeout=10
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Direct connection successful!")
        print(f"   PostgreSQL version: {version[:60]}...")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Direct connection failed: {str(e)[:200]}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check if database server is running")
        print("   2. Verify hostname is accessible from this machine")
        print("   3. Check firewall/network settings")
        print("   4. Verify database credentials")
        return False

    # Try to connect using SQLAlchemy
    print("\n🔌 Testing SQLAlchemy connection...")
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={
                'connect_timeout': 10
            }
        )

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ SQLAlchemy connection successful!")

            # Check if users table exists
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.fetchone()[0]
                print(f"✅ 'users' table exists with {count} records")
            except Exception as e:
                print(f"⚠️ 'users' table does not exist: {str(e)[:100]}")
                print("   This is normal for first-time setup")

    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {str(e)[:200]}")
        return False

    print("\n" + "=" * 60)
    print("✅ DATABASE CONNECTION CHECK PASSED!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = check_database_connection()
    sys.exit(0 if success else 1)
