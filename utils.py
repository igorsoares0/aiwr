from flask import current_app
from flask_mail import Mail, Message
import secrets
import string
import requests

mail = Mail()

def send_email_mailgun(subject, recipient, html_body, sender=None):
    """
    Send an email using Mailgun API

    Args:
        subject (str): Email subject
        recipient (str): Recipient email address
        html_body (str): HTML content of the email
        sender (str, optional): Sender email address. Defaults to config value.

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        mailgun_api_key = current_app.config.get('MAILGUN_API_KEY')
        mailgun_domain = current_app.config.get('MAILGUN_DOMAIN')
        mailgun_base_url = current_app.config.get('MAILGUN_API_BASE_URL', 'https://api.mailgun.net/v3')

        if not mailgun_api_key or not mailgun_domain:
            current_app.logger.error('Mailgun API key or domain not configured')
            return False

        if sender is None:
            sender = current_app.config.get('MAIL_DEFAULT_SENDER')

        # Mailgun API endpoint
        url = f"{mailgun_base_url}/{mailgun_domain}/messages"

        # Prepare email data
        data = {
            'from': sender,
            'to': recipient,
            'subject': subject,
            'html': html_body
        }

        # Send request to Mailgun API
        response = requests.post(
            url,
            auth=('api', mailgun_api_key),
            data=data,
            timeout=10
        )

        # Check response
        if response.status_code == 200:
            current_app.logger.info(f'Email sent successfully to {recipient} via Mailgun')
            return True
        else:
            current_app.logger.error(
                f'Mailgun API error: {response.status_code} - {response.text}'
            )
            return False

    except requests.exceptions.Timeout:
        current_app.logger.error('Mailgun API request timed out')
        return False
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Mailgun API request failed: {str(e)}')
        return False
    except Exception as e:
        current_app.logger.error(f'Error sending email via Mailgun: {str(e)}')
        return False

def send_email_smtp(subject, recipient, html_body):
    """
    Send an email using Flask-Mail (SMTP) - Legacy/Fallback method

    Args:
        subject (str): Email subject
        recipient (str): Recipient email address
        html_body (str): HTML content of the email

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        current_app.logger.info(f'Email sent successfully to {recipient} via SMTP')
        return True
    except Exception as e:
        current_app.logger.error(f'Error sending email via SMTP: {str(e)}')
        return False

def send_email(subject, recipient, html_body):
    """
    Send an email using configured method (Mailgun API or SMTP)

    This function automatically chooses between Mailgun API (production)
    or SMTP (development/fallback) based on configuration.

    Args:
        subject (str): Email subject
        recipient (str): Recipient email address
        html_body (str): HTML content of the email

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    use_mailgun = current_app.config.get('USE_MAILGUN_API', True)

    if use_mailgun:
        # Try Mailgun API first
        success = send_email_mailgun(subject, recipient, html_body)

        # If Mailgun fails and SMTP is configured, try SMTP as fallback
        if not success and current_app.config.get('MAIL_SERVER'):
            current_app.logger.warning('Mailgun failed, attempting SMTP fallback...')
            success = send_email_smtp(subject, recipient, html_body)

        return success
    else:
        # Use SMTP directly
        return send_email_smtp(subject, recipient, html_body)

def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))