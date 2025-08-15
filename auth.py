from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from google.oauth2 import id_token
from google.auth.transport import requests
from models import db, User, PasswordResetToken, EmailVerificationToken
from forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from utils import send_email
from google_auth_utils import GoogleAuthValidator
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            if not user.email_verified:
                flash('Please verify your email address before logging in.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip()
        )
        user.set_password(form.password.data)
        
        # Start 7-day trial automatically
        user.start_trial()
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            verification_token = EmailVerificationToken(user.id)
            db.session.add(verification_token)
            db.session.commit()
            
            email_sent = send_verification_email(user, verification_token.token)
            
            if email_sent:
                flash('Registration successful! Please check your email to verify your account.', 'success')
            else:
                flash('Registration successful! However, we could not send the verification email. Please contact support.', 'warning')
            
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    token = request.form.get('credential')
    if not token:
        current_app.logger.warning(f"Google login attempt without token from IP: {request.remote_addr}")
        flash('Google authentication failed. No credential received.', 'error')
        return redirect(url_for('auth.login'))
    
    # Validate configuration first
    config_valid, config_msg = GoogleAuthValidator.validate_client_configuration()
    if not config_valid:
        current_app.logger.error(f"Google OAuth configuration error: {config_msg}")
        flash('Google authentication is not properly configured. Please contact support.', 'error')
        return redirect(url_for('auth.login'))
    
    # Validate token structure
    token_valid, token_msg = GoogleAuthValidator.validate_token_structure(token)
    if not token_valid:
        current_app.logger.warning(f"Invalid Google token structure: {token_msg} from IP: {request.remote_addr}")
        flash('Invalid authentication token received.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), current_app.config['GOOGLE_CLIENT_ID']
        )
        
        # Validate the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            current_app.logger.warning(f"Invalid Google token issuer: {idinfo.get('iss')} from IP: {request.remote_addr}")
            flash('Invalid Google token.', 'error')
            return redirect(url_for('auth.login'))
        
        # Extract and validate user information
        user_info = GoogleAuthValidator.extract_user_info_safely(idinfo)
        
        current_app.logger.info(f"Google authentication successful for email: {user_info['email']}")
        GoogleAuthValidator.log_authentication_attempt(user_info['email'], True)
        
        # Find or create user
        user = User.query.filter_by(google_id=user_info['google_id']).first()
        if not user:
            user = User.query.filter_by(email=user_info['email']).first()
            if user:
                # Link existing account with Google
                current_app.logger.info(f"Linking existing account {user_info['email']} with Google ID: {user_info['google_id']}")
                user.google_id = user_info['google_id']
                user.avatar_url = user_info['avatar_url']
                user.email_verified = True
            else:
                # Create new user
                current_app.logger.info(f"Creating new Google user: {user_info['email']}")
                user = User(
                    email=user_info['email'],
                    first_name=user_info['first_name'],
                    last_name=user_info['last_name'],
                    google_id=user_info['google_id'],
                    avatar_url=user_info['avatar_url'],
                    email_verified=True
                )
                # Start 7-day trial automatically for new Google users
                user.start_trial()
            
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as db_error:
                db.session.rollback()
                current_app.logger.error(f"Database error during Google login for {user_info['email']}: {str(db_error)}")
                GoogleAuthValidator.log_authentication_attempt(user_info['email'], False, f"Database error: {str(db_error)}")
                flash('An error occurred while creating your account. Please try again.', 'error')
                return redirect(url_for('auth.login'))
        
        # Log successful login
        login_user(user, remember=True)
        current_app.logger.info(f"User {user_info['email']} logged in successfully via Google")
        
        # Check for next parameter
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):  # Security: only allow relative URLs
            return redirect(next_page)
        
        return redirect(url_for('main.dashboard'))
        
    except ValueError as e:
        error_msg = str(e)
        current_app.logger.warning(f"Google token verification failed: {error_msg} from IP: {request.remote_addr}")
        GoogleAuthValidator.log_authentication_attempt("unknown", False, error_msg)
        
        if 'Invalid token' in error_msg or 'expired' in error_msg.lower():
            flash('The Google authentication token is invalid or expired. Please try again.', 'error')
        elif 'Wrong issuer' in error_msg:
            flash('Invalid authentication source. Please try again.', 'error')
        elif 'missing' in error_msg.lower():
            flash('Required information is missing from Google. Please try again.', 'error')
        else:
            flash('Google authentication failed. Please try again.', 'error')
            
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error during Google authentication: {str(e)} from IP: {request.remote_addr}")
        GoogleAuthValidator.log_authentication_attempt("unknown", False, f"Unexpected error: {str(e)}")
        flash('An unexpected error occurred during Google authentication. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Invalidate any existing reset tokens
            existing_tokens = PasswordResetToken.query.filter_by(user_id=user.id, used=False).all()
            for token in existing_tokens:
                token.used = True
            
            # Create new reset token
            reset_token = PasswordResetToken(user.id)
            db.session.add(reset_token)
            db.session.commit()
            
            send_password_reset_email(user, reset_token.token)
        
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    if not reset_token or not reset_token.is_valid:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = reset_token.user
        user.set_password(form.password.data)
        reset_token.used = True
        
        db.session.commit()
        
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    verification_token = EmailVerificationToken.query.filter_by(token=token).first()
    if not verification_token or not verification_token.is_valid:
        flash('Invalid or expired verification token.', 'error')
        return redirect(url_for('auth.login'))
    
    user = verification_token.user
    user.email_verified = True
    verification_token.used = True
    
    db.session.commit()
    
    flash('Your email has been verified successfully!', 'success')
    return redirect(url_for('auth.login'))

def send_verification_email(user, token):
    subject = 'Verify Your Writify Account'
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    html_body = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Welcome to Writify!</h2>
        <p>Hi {user.first_name},</p>
        <p>Thank you for registering with Writify. Please click the button below to verify your email address:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_url}" style="background-color: #000; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email</a>
        </div>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p><a href="{verify_url}">{verify_url}</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>Best regards,<br>The Writify Team</p>
    </div>
    '''
    
    return send_email(subject, user.email, html_body)

def send_password_reset_email(user, token):
    subject = 'Reset Your Writify Password'
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    html_body = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Reset Your Password</h2>
        <p>Hi {user.first_name},</p>
        <p>You requested to reset your password for your Writify account. Click the button below to reset it:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #000; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
        </div>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this password reset, please ignore this email.</p>
        <p>Best regards,<br>The Writify Team</p>
    </div>
    '''
    
    send_email(subject, user.email, html_body)

