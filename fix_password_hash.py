#!/usr/bin/env python
"""
Fix password_hash column length in production database
Run this script to update the existing users table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def fix_password_hash_length():
    """Increase password_hash column length from 128 to 256"""
    database_url = os.environ.get('DATABASE_URL', '')

    if not database_url:
        print("❌ ERROR: DATABASE_URL not set!")
        return False

    # Fix URL format if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print("🔧 Connecting to database...")
    print(f"📊 Database: {database_url[:50]}...")

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            print("✅ Connected to database")

            # Check current column type
            print("\n🔍 Checking current password_hash column...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'password_hash'
            """))

            row = result.fetchone()
            if row:
                print(f"   Current type: {row[1]}")
                print(f"   Current length: {row[2]}")

            # Alter column
            print("\n🔧 Altering password_hash column to VARCHAR(256)...")
            conn.execute(text("""
                ALTER TABLE users
                ALTER COLUMN password_hash TYPE VARCHAR(256)
            """))
            conn.commit()

            print("✅ Column altered successfully!")

            # Verify change
            print("\n✅ Verifying change...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'password_hash'
            """))

            row = result.fetchone()
            if row:
                print(f"   New type: {row[1]}")
                print(f"   New length: {row[2]}")

            print("\n" + "="*60)
            print("✅ PASSWORD_HASH COLUMN UPDATED SUCCESSFULLY!")
            print("="*60)
            return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    success = fix_password_hash_length()
    sys.exit(0 if success else 1)
