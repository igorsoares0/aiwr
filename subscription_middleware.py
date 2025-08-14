from functools import wraps
from flask import request, redirect, url_for, jsonify, flash
from flask_login import current_user
from datetime import datetime

def subscription_required(f):
    """Decorator to require active subscription or trial"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Check if user has valid access (trial or paid)
        if not current_user.has_valid_access:
            # If trial expired, redirect to pricing
            if current_user.subscription_status in ['trial', 'trial_expired']:
                flash('Your free trial has expired. Please choose a plan to continue.', 'warning')
                return redirect(url_for('billing.pricing'))
            
            # If subscription inactive, redirect to pricing
            elif current_user.subscription_status in ['canceled', 'incomplete', 'past_due']:
                flash('Your subscription is inactive. Please update your payment method or choose a new plan.', 'warning')
                return redirect(url_for('billing.pricing'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def api_subscription_required(f):
    """Decorator for API endpoints to require active subscription or trial"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has valid access
        if not current_user.has_valid_access:
            return jsonify({
                'error': 'Subscription required',
                'subscription_status': current_user.subscription_status,
                'trial_expired': current_user.subscription_status == 'trial' and not current_user.is_trial_active,
                'redirect_url': url_for('billing.pricing')
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def check_trial_status():
    """Check and update trial status for authenticated users"""
    if current_user.is_authenticated:
        # Auto-expire trial if time is up
        if (current_user.subscription_status == 'trial' and 
            current_user.trial_ends_at and 
            current_user.trial_ends_at < datetime.utcnow()):
            
            current_user.subscription_status = 'trial_expired'
            from models import db
            db.session.commit()

def get_subscription_context():
    """Get subscription context for templates"""
    if not current_user.is_authenticated:
        return {}
    
    context = {
        'subscription_status': current_user.subscription_status,
        'subscription_plan': current_user.subscription_plan,
        'is_trial_active': current_user.is_trial_active,
        'is_subscription_active': current_user.is_subscription_active,
        'has_valid_access': current_user.has_valid_access,
        'days_left_in_trial': current_user.days_left_in_trial if current_user.is_trial_active else 0,
        'trial_ends_at': current_user.trial_ends_at,
        'subscription_ends_at': current_user.subscription_ends_at,
    }
    
    # Add subscription details if available
    current_subscription = current_user.get_current_subscription()
    if current_subscription:
        context.update({
            'current_subscription': {
                'status': current_subscription.status,
                'plan_type': current_subscription.plan_type,
                'current_period_end': current_subscription.current_period_end,
                'days_until_renewal': current_subscription.days_until_renewal,
                'is_canceled': current_subscription.is_canceled,
                'canceled_at': current_subscription.canceled_at,
            }
        })
    
    return context

def init_subscription_middleware(app):
    """Initialize subscription middleware with Flask app"""
    
    @app.before_request
    def before_request():
        # Skip for auth routes, static files, and webhooks
        if (request.endpoint and 
            (request.endpoint.startswith('auth.') or 
             request.endpoint.startswith('static') or
             request.endpoint == 'billing.webhook')):
            return
        
        # Check trial status
        check_trial_status()
    
    @app.context_processor
    def inject_subscription_context():
        """Make subscription context available in all templates"""
        return get_subscription_context()

# Usage limits - can be expanded later
class UsageLimits:
    @staticmethod
    def get_text_limit(user):
        """Get maximum number of texts user can create"""
        if user.has_valid_access:
            return 1000  # Unlimited for paid users
        return 3  # Limited for expired users
    
    @staticmethod
    def get_document_limit(user):
        """Get maximum number of documents user can upload"""
        if user.has_valid_access:
            return 1000  # Unlimited for paid users
        return 5  # Limited for expired users
    
    @staticmethod
    def get_ai_requests_limit(user):
        """Get maximum AI requests per day"""
        if user.has_valid_access:
            return 500  # High limit for paid users
        return 10  # Very limited for expired users
    
    @staticmethod
    def can_create_text(user):
        """Check if user can create more texts"""
        current_count = user.texts.count()
        return current_count < UsageLimits.get_text_limit(user)
    
    @staticmethod
    def can_upload_document(user):
        """Check if user can upload more documents"""
        current_count = user.documents.count()
        return current_count < UsageLimits.get_document_limit(user)