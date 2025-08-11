#!/usr/bin/env python3
"""
Migration runner script for Writify
Run this to execute all database migrations
"""

import os
import subprocess
import sys
from app import create_app
from flask_migrate import upgrade

def run_migrations():
    """Run Flask-Migrate upgrade"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Running database migrations...")
        try:
            upgrade()
            print("✅ Migrations completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

def check_migration_files():
    """Check if migration files exist"""
    migrations_dir = "migrations/versions"
    if not os.path.exists(migrations_dir):
        print("❌ Migrations directory not found!")
        print("Run 'flask db init' first to initialize migrations")
        return False
    
    migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
    print(f"📁 Found {len(migration_files)} migration files:")
    for f in migration_files:
        print(f"   - {f}")
    
    return len(migration_files) > 0

if __name__ == '__main__':
    print("🚀 Writify Database Migration Tool")
    print("=" * 40)
    
    # Check if migration files exist
    if not check_migration_files():
        print("\nTo create initial migration:")
        print("1. flask db init (if not done yet)")  
        print("2. flask db migrate -m 'Initial migration'")
        sys.exit(1)
    
    # Run migrations
    if run_migrations():
        print("\n🎉 Database is ready!")
        print("You can now run: python init_database.py")
    else:
        print("\n💡 If you're getting errors, try:")
        print("1. Check your DATABASE_URL in .env")
        print("2. Make sure PostgreSQL is running")
        print("3. Verify database permissions")
        sys.exit(1)