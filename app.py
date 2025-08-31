import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from models import db, User
from auth import auth_bp
from main import main_bp
from billing_routes import billing_bp
from utils import mail
from config import Config
from subscription_middleware import init_subscription_middleware

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    # Create database tables on startup (for production deployment)
    with app.app_context():
        try:
            print("🔍 Checking if database tables exist...")
            # Try to query users table
            from sqlalchemy import text
            db.session.execute(text("SELECT 1 FROM users LIMIT 1")).fetchone()
            print("✅ Database tables already exist")
        except Exception as e:
            print(f"⚠️ Tables missing: {str(e)}")
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Initialize with admin user in new session
            try:
                print("👤 Creating admin user...")
                # Start fresh session after table creation
                db.session.commit()  # Commit table creation
                
                from werkzeug.security import generate_password_hash
                import datetime
                
                admin_user = User.query.filter_by(email='admin@writify.com').first()
                if not admin_user:
                    admin_user = User(
                        email='admin@writify.com',
                        password_hash=generate_password_hash('admin123456'),
                        first_name='Admin',
                        last_name='User',
                        is_active=True,
                        email_verified=True,
                        subscription_status='trial',
                        trial_ends_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("✅ Admin user created: admin@writify.com / admin123456")
                else:
                    print("ℹ️ Admin user already exists")
            except Exception as init_error:
                print(f"⚠️ Could not create admin user: {init_error}")
                try:
                    db.session.rollback()
                except:
                    pass
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialize subscription middleware
    init_subscription_middleware(app)
    
    # Make app config available in templates
    @app.context_processor
    def inject_config():
        """Make app configuration available in templates"""
        return {
            'config': {
                'GOOGLE_CLIENT_ID': app.config.get('GOOGLE_CLIENT_ID'),
                'DEBUG': app.debug
            }
        }
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(billing_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Security headers
    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://gsi.google.com https://www.google.com https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com https://checkout.stripe.com https://js.stripe.com https://billing.stripe.com"
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)