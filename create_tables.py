#!/usr/bin/env python3
"""
Script to create database tables directly - for Render deployment
"""
import os
from app import create_app
from models import db
from dotenv import load_dotenv

def create_tables():
    """Create all database tables"""
    load_dotenv()
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # List created tables
        from sqlalchemy import text
        result = db.session.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]
        print(f"📋 Created tables: {', '.join(tables)}")

if __name__ == "__main__":
    create_tables()