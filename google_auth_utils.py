"""
Google OAuth utilities for enhanced security and validation
"""

import time
import requests
from flask import current_app
from typing import Dict, Optional, Tuple


class GoogleAuthValidator:
    """Enhanced validation for Google OAuth tokens"""
    
    @staticmethod
    def validate_token_structure(token: str) -> Tuple[bool, str]:
        """
        Validate basic token structure before sending to Google
        """
        if not token:
            return False, "Token is empty"
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return False, "Invalid JWT structure"
        
        # Check reasonable length (Google JWTs are typically 800-2000 characters)
        if len(token) < 100 or len(token) > 3000:
            return False, "Token length is suspicious"
        
        return True, "Token structure is valid"
    
    @staticmethod
    def validate_client_configuration() -> Tuple[bool, str]:
        """
        Validate that Google OAuth is properly configured
        """
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id:
            return False, "Google Client ID not configured"
        
        if not client_secret:
            return False, "Google Client Secret not configured"
        
        # Validate Client ID format (should end with .apps.googleusercontent.com)
        if not client_id.endswith('.apps.googleusercontent.com'):
            return False, "Invalid Google Client ID format"
        
        # Validate Client Secret format (should start with GOCSPX-)
        if not client_secret.startswith('GOCSPX-'):
            return False, "Invalid Google Client Secret format"
        
        return True, "Configuration is valid"
    
    @staticmethod
    def extract_user_info_safely(idinfo: Dict) -> Dict:
        """
        Safely extract user information from Google ID token
        """
        user_info = {
            'google_id': idinfo.get('sub', ''),
            'email': idinfo.get('email', '').lower(),
            'first_name': idinfo.get('given_name', ''),
            'last_name': idinfo.get('family_name', ''),
            'avatar_url': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False),
            'locale': idinfo.get('locale', ''),
            'issued_at': idinfo.get('iat', 0),
            'expires_at': idinfo.get('exp', 0)
        }
        
        # Validate required fields
        if not user_info['google_id']:
            raise ValueError("Google ID (sub) is missing from token")
        
        if not user_info['email']:
            raise ValueError("Email is missing from token")
        
        # Validate email format
        if '@' not in user_info['email']:
            raise ValueError("Invalid email format from Google")
        
        # Check token expiration
        current_time = int(time.time())
        if user_info['expires_at'] and current_time > user_info['expires_at']:
            raise ValueError("Google token has expired")
        
        return user_info
    
    @staticmethod
    def log_authentication_attempt(email: str, success: bool, error_msg: str = None):
        """
        Log authentication attempts for security monitoring
        """
        log_data = {
            'email': email,
            'success': success,
            'timestamp': time.time(),
            'user_agent': None,
            'ip_address': None
        }
        
        try:
            from flask import request
            log_data['user_agent'] = request.headers.get('User-Agent', '')
            log_data['ip_address'] = request.remote_addr
        except:
            pass  # Outside request context
        
        if success:
            current_app.logger.info(f"Google auth success: {email} from {log_data['ip_address']}")
        else:
            current_app.logger.warning(f"Google auth failed: {email} - {error_msg} from {log_data['ip_address']}")


def validate_google_domain_access() -> Tuple[bool, str]:
    """
    Test connectivity to Google services
    """
    test_urls = [
        'https://accounts.google.com/.well-known/openid_configuration',
        'https://www.googleapis.com/oauth2/v3/certs'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return False, f"Cannot reach {url} - Status: {response.status_code}"
        except requests.RequestException as e:
            return False, f"Network error accessing {url}: {str(e)}"
    
    return True, "Google services are accessible"


