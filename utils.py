from flask import current_app
from flask_mail import Mail, Message
import secrets
import string

mail = Mail()

def send_email(subject, recipient, html_body):
    """Send an email using Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Error sending email: {str(e)}')
        return False

def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))