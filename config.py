import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get and validate database URL with proper error handling"""
    database_url = os.environ.get('DATABASE_URL', '').strip()

    # Check if URL is empty or None
    if not database_url:
        print("⚠️ WARNING: DATABASE_URL environment variable is not set!")
        print("⚠️ Using fallback local PostgreSQL connection")
        return 'postgresql://localhost/writify_db'

    # Fix for Render.com: Replace postgres:// with postgresql://
    if database_url.startswith('postgres://'):
        print("🔧 Converting postgres:// to postgresql:// for SQLAlchemy compatibility")
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    # Validate URL format
    if not (database_url.startswith('postgresql://') or database_url.startswith('postgres://')):
        print(f"⚠️ WARNING: Invalid DATABASE_URL format: {database_url[:30]}...")
        print("⚠️ Using fallback local PostgreSQL connection")
        return 'postgresql://localhost/writify_db'

    print(f"✅ Database URL configured: {database_url[:50]}...")
    return database_url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Get database URL with validation
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database engine configuration for PostgreSQL (Neon DB, Render, etc.)
    # Optimized for serverless PostgreSQL like Neon
    _connect_args = {
        'connect_timeout': 10,
        'application_name': 'writify_app',
    }

    # Add SSL mode if DATABASE_URL contains sslmode parameter (for Neon DB)
    _db_url = os.environ.get('DATABASE_URL', '')
    if 'sslmode' not in _db_url and _db_url.startswith('postgresql://'):
        # If no sslmode specified but using PostgreSQL, default to prefer
        _connect_args['sslmode'] = 'prefer'

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Check connections before using
        'pool_recycle': 300,    # Recycle connections every 5 min
        'pool_size': 5,         # Smaller pool for serverless (Neon optimized)
        'max_overflow': 10,     # Max overflow connections
        'pool_timeout': 30,     # Timeout waiting for connection
        'connect_args': _connect_args
    }
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Mailgun API settings (Production - Recommended)
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_BASE_URL = os.environ.get('MAILGUN_API_BASE_URL') or 'https://api.mailgun.net/v3'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'contact@prosewrites.com'

    # Legacy SMTP settings (Fallback for development/testing)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Email configuration mode
    USE_MAILGUN_API = os.environ.get('USE_MAILGUN_API', 'True').lower() in ['true', 'on', '1']
    
    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # Security
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour