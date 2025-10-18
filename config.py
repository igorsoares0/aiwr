import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database URL with proper handling
    database_url = os.environ.get('DATABASE_URL')

    # Validate and fix database URL
    if not database_url:
        # No DATABASE_URL provided - use local default
        print("⚠️ WARNING: DATABASE_URL not set, using local PostgreSQL")
        database_url = 'postgresql://localhost/writify_db'
    elif database_url.strip() == '':
        # Empty DATABASE_URL - use local default
        print("⚠️ WARNING: DATABASE_URL is empty, using local PostgreSQL")
        database_url = 'postgresql://localhost/writify_db'
    else:
        # Fix for Render.com: Replace postgres:// with postgresql:// if needed
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database engine configuration for Render PostgreSQL
    # More robust SSL configuration
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'writify_app',
            'options': '-c statement_timeout=30000'
        }
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