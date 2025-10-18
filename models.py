from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import bcrypt
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)  # Increased from 128 to support bcrypt/scrypt hashes
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    avatar_url = db.Column(db.String(200), nullable=True)
    
    # Subscription fields
    subscription_status = db.Column(db.String(20), nullable=False, default='trial')  # trial, active, past_due, canceled, incomplete
    subscription_plan = db.Column(db.String(20), nullable=True)  # monthly, annual
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    trial_ends_at = db.Column(db.DateTime, nullable=True)
    subscription_ends_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    email_tokens = db.relationship('EmailVerificationToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    texts = db.relationship('Text', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    payment_events = db.relationship('PaymentEvent', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        if password:
            salt = bcrypt.gensalt()
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the user's password"""
        if not self.password_hash or not password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_id(self):
        return str(self.id)
    
    # Subscription methods
    def start_trial(self):
        """Start a 7-day free trial"""
        self.subscription_status = 'trial'
        self.trial_ends_at = datetime.utcnow() + timedelta(days=7)
        
    @property
    def is_trial_active(self):
        """Check if trial is still active"""
        return (self.subscription_status == 'trial' and 
                self.trial_ends_at and 
                self.trial_ends_at > datetime.utcnow())
    
    @property
    def is_subscription_active(self):
        """Check if user has active subscription"""
        return self.subscription_status == 'active'
    
    @property
    def has_valid_access(self):
        """Check if user has valid access (trial or paid)"""
        return self.is_trial_active or self.is_subscription_active
    
    @property
    def days_left_in_trial(self):
        """Get days remaining in trial"""
        if not self.is_trial_active:
            return 0
        return (self.trial_ends_at - datetime.utcnow()).days
    
    def get_current_subscription(self):
        """Get the current active subscription"""
        return self.subscriptions.filter_by(status='active').first()
    
    def __repr__(self):
        return f'<User {self.email}>'

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, expires_in_hours=1):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.used and not self.is_expired

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, expires_in_hours=24):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.used and not self.is_expired

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf' or 'docx'
    file_size = db.Column(db.Integer, nullable=False)
    content_text = db.Column(db.Text, nullable=True)  # Extracted text content
    upload_path = db.Column(db.String(500), nullable=True)  # Local path for backward compatibility
    
    # Cloudinary fields
    cloudinary_public_id = db.Column(db.String(255), nullable=True)
    cloudinary_url = db.Column(db.String(500), nullable=True)
    cloudinary_secure_url = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_cloudinary_stored(self):
        """Check if document is stored in Cloudinary"""
        return bool(self.cloudinary_public_id and self.cloudinary_secure_url)
    
    @property
    def file_url(self):
        """Get file URL - prefer Cloudinary secure URL"""
        if self.is_cloudinary_stored:
            return self.cloudinary_secure_url
        return self.upload_path  # Fallback to local path
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'

# Association table for Text-Document many-to-many relationship
text_documents = db.Table('text_documents',
    db.Column('text_id', db.Integer, db.ForeignKey('texts.id'), primary_key=True),
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Text(db.Model):
    __tablename__ = 'texts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with documents
    documents = db.relationship('Document', secondary=text_documents, backref='texts', lazy='dynamic')
    
    def __repr__(self):
        return f'<Text {self.title}>'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stripe_subscription_id = db.Column(db.String(100), nullable=False, unique=True)
    stripe_price_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # active, past_due, canceled, incomplete, trialing
    plan_type = db.Column(db.String(20), nullable=False)  # monthly, annual
    current_period_start = db.Column(db.DateTime, nullable=False)
    current_period_end = db.Column(db.DateTime, nullable=False)
    trial_start = db.Column(db.DateTime, nullable=True)
    trial_end = db.Column(db.DateTime, nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_active(self):
        """Check if subscription is active"""
        return self.status in ['active', 'trialing']
    
    @property
    def is_past_due(self):
        """Check if subscription is past due"""
        return self.status == 'past_due'
    
    @property
    def is_canceled(self):
        """Check if subscription is canceled"""
        return self.status == 'canceled' or self.canceled_at is not None
    
    @property
    def days_until_renewal(self):
        """Get days until next renewal"""
        if not self.current_period_end:
            return 0
        return (self.current_period_end - datetime.utcnow()).days
    
    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id}>'

class PaymentEvent(db.Model):
    __tablename__ = 'payment_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for system events
    stripe_event_id = db.Column(db.String(100), nullable=False, unique=True)
    event_type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Store event data for debugging
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_processed(self):
        """Check if event has been processed"""
        return self.processed_at is not None
    
    def mark_processed(self):
        """Mark event as processed"""
        self.processed_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<PaymentEvent {self.stripe_event_id}>'