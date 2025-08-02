from functools import wraps
from flask import request, abort, current_app, session
from flask_login import current_user
import time
from collections import defaultdict
from datetime import datetime, timedelta
import re

# Rate limiting storage (in production, use Redis)
rate_limit_storage = defaultdict(list)

def rate_limit(max_requests=5, per_seconds=60, key_func=None):
    """
    Rate limiting decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr
                
            now = time.time()
            # Clean old requests
            rate_limit_storage[key] = [
                req_time for req_time in rate_limit_storage[key] 
                if now - req_time < per_seconds
            ]
            
            if len(rate_limit_storage[key]) >= max_requests:
                abort(429)  # Too Many Requests
                
            rate_limit_storage[key].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_email(email):
    """
    Validate email format with additional security checks
    """
    if not email or len(email) > 254:
        return False
        
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
        
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\.{2,}',  # Multiple consecutive dots
        r'^\.|\.$',  # Starting or ending with dot
        r'@.*@',  # Multiple @ symbols
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, email):
            return False
            
    return True

def validate_password_strength(password):
    """
    Validate password strength
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"
        
    if len(password) > 128:
        return False, "Password is too long"
        
    # Check for at least one uppercase, lowercase, and number
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
        
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
        
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
        
    # Check for common weak passwords
    weak_passwords = [
        'password', '12345678', 'qwerty123', 'abc12345',
        'password123', '123456789', 'welcome123'
    ]
    
    if password.lower() in weak_passwords:
        return False, "Password is too common"
        
    return True, "Password is strong"

def check_password_breach(password):
    """
    Check if password has been breached (placeholder for Have I Been Pwned API)
    In production, integrate with Have I Been Pwned API
    """
    # This is a placeholder - in production, implement HIBP API check
    return False

def sanitize_input(text, max_length=1000):
    """
    Sanitize user input
    """
    if not text:
        return ""
        
    # Remove potential XSS attempts
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
        
    return text.strip()

def require_fresh_login(f):
    """
    Decorator to require a fresh login for sensitive operations
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
            
        # Check if login is fresh (within last 30 minutes)
        if 'login_time' not in session:
            abort(401)
            
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.utcnow() - login_time > timedelta(minutes=30):
            session.pop('login_time', None)
            abort(401)
            
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, details=None, user_id=None):
    """
    Log security events for monitoring
    """
    timestamp = datetime.utcnow().isoformat()
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'user_id': user_id,
        'details': details or {}
    }
    
    # In production, send to proper logging system
    current_app.logger.warning(f"Security Event: {log_entry}")

class SecurityHeaders:
    """
    Security headers middleware
    """
    @staticmethod
    def init_app(app):
        @app.after_request
        def set_security_headers(response):
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # HSTS (HTTPS only)
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://cdn.tailwindcss.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://accounts.google.com; "
                "frame-src https://accounts.google.com;"
            )
            response.headers['Content-Security-Policy'] = csp
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            return response