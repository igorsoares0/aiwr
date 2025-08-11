#!/usr/bin/env python3
"""
Database initialization script for Writify
Run this script AFTER running Flask-Migrate commands
"""

import os
import sys
from app import create_app
from models import db, User

def init_database():
    """Initialize database with admin user after migrations"""
    app = create_app()
    
    with app.app_context():
        print("Checking database connection...")
        
        # Create a test admin user (optional)
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@writify.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        
        try:
            existing_admin = User.query.filter_by(email=admin_email).first()
            if not existing_admin:
                admin_user = User(
                    email=admin_email,
                    first_name='Admin',
                    last_name='User',
                    email_verified=True,
                    is_active=True
                )
                admin_user.set_password(admin_password)
                # Start trial for admin user
                admin_user.start_trial()
                
                db.session.add(admin_user)
                db.session.commit()
                
                print(f"✅ Admin user created: {admin_email}")
                print(f"🔑 Admin password: {admin_password}")
                print(f"📅 Trial started: 7 days from now")
            else:
                print("ℹ️  Admin user already exists")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("\nIf you see column errors, make sure to run migrations first:")
            print("flask db upgrade")
            sys.exit(1)
            
        print("✅ Database initialization completed!")

if __name__ == '__main__':
    init_database()