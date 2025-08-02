from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from google.oauth2 import id_token
from google.auth.transport import requests
from models import db, User, PasswordResetToken, EmailVerificationToken
from forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from utils import send_email
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
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            verification_token = EmailVerificationToken(user.id)
            db.session.add(verification_token)
            db.session.commit()
            
            send_verification_email(user, verification_token.token)
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    token = request.form.get('credential')
    if not token:
        flash('Google authentication failed.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), current_app.config['GOOGLE_CLIENT_ID']
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            flash('Invalid Google token.', 'error')
            return redirect(url_for('auth.login'))
        
        google_id = idinfo['sub']
        email = idinfo['email'].lower()
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        avatar_url = idinfo.get('picture', '')
        
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # Link existing account with Google
                user.google_id = google_id
                user.avatar_url = avatar_url
                user.email_verified = True
            else:
                # Create new user
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id,
                    avatar_url=avatar_url,
                    email_verified=True
                )
            
            db.session.add(user)
            db.session.commit()
        
        login_user(user, remember=True)
        return redirect(url_for('main.dashboard'))
        
    except ValueError as e:
        flash('Google authentication failed.', 'error')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash('An error occurred during Google authentication.', 'error')
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
    
    send_email(subject, user.email, html_body)

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