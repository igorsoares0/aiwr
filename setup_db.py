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

def setup_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a test admin user (optional)
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@writify.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        
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
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"Admin user created: {admin_email}")
            print(f"Admin password: {admin_password}")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    setup_database()