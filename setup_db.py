#!/usr/bin/env python3
"""
Database setup script for Writify
Run this script to initialize the database
"""

import os
import sys
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def add_subscription_columns():
    """Add subscription columns to users table if they don't exist"""
    try:
        # Check if subscription_status column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'subscription_status';
        """))
        
        if result.fetchone():
            print("✅ Subscription columns already exist")
            return
        
        print("📝 Adding subscription columns to users table...")
        
        # Add subscription columns
        db.session.execute(text("ALTER TABLE users ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'trial';"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN subscription_plan VARCHAR(20);"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN trial_ends_at TIMESTAMP;"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN subscription_ends_at TIMESTAMP;"))
        
        db.session.commit()
        print("✅ Subscription columns added successfully")
        
    except Exception as e:
        print(f"Note: Could not add subscription columns: {str(e)}")
        db.session.rollback()

def setup_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Add subscription columns if needed
        add_subscription_columns()
        
        # Create a test admin user (optional)
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@writify.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        
        # Now try to create admin user (columns should exist now)
        try:
            existing_admin = User.query.filter_by(email=admin_email).first()
            if existing_admin:
                print("Admin user already exists")
                return
        except Exception as e:
            print(f"Note: Still having column issues: {str(e)}")
            db.session.rollback()
        
        # Create admin user
        try:
            admin_user = User(
                email=admin_email,
                first_name='Admin',
                last_name='User',
                email_verified=True,
                is_active=True
            )
            admin_user.set_password(admin_password)
            admin_user.start_trial()  # Should work now
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"✅ Admin user created: {admin_email}")
            print(f"🔑 Admin password: {admin_password}")
            print(f"📅 Trial started: 7 days")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Could not create admin user: {str(e)}")
            print("💡 Try running the script again or check your database connection")

if __name__ == '__main__':
    setup_database()