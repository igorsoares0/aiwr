# Writify - AI-Powered Writing Assistant

A complete, secure, and production-ready login system built with Flask, featuring email/password authentication, Google OAuth, and password recovery functionality.

## Features

- ✅ **Secure Authentication System**
  - Email/password registration and login
  - Google OAuth integration
  - Email verification
  - Password recovery with secure tokens
  - Session management with Flask-Login

- ✅ **Modern UI Design**
  - Responsive design with Tailwind CSS
  - Clean, professional interface matching the provided mockups
  - Mobile-friendly authentication forms
  - Elegant dashboard interface

- ✅ **Security Features**
  - Password hashing with bcrypt
  - CSRF protection
  - Rate limiting
  - Security headers (CSP, HSTS, etc.)
  - Input validation and sanitization
  - SQL injection prevention with SQLAlchemy ORM

- ✅ **Production Ready**
  - PostgreSQL database support
  - Email integration with Mailtrap for testing
  - Error handling and logging
  - Database migrations with Flask-Migrate
  - Environment-based configuration

## Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js (for Tailwind CSS - optional, using CDN)

## Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd aiwr
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@localhost/writify_db
   
   # Google OAuth (get from Google Cloud Console)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   # Mailtrap settings
   MAIL_SERVER=sandbox.smtp.mailtrap.io
   MAIL_PORT=2525
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-mailtrap-username
   MAIL_PASSWORD=your-mailtrap-password
   MAIL_DEFAULT_SENDER=noreply@writify.com
   ```

3. **Set up PostgreSQL database:**
   ```bash
   # Create database
   createdb writify_db
   
   # Run database setup
   python setup_db.py
   ```

4. **Set up Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - `http://localhost:5000/auth/google-login` (development)
     - `https://yourdomain.com/auth/google-login` (production)

5. **Set up Mailtrap:**
   - Sign up at [Mailtrap](https://mailtrap.io)
   - Get your SMTP credentials from the inbox settings
   - Update the `.env` file with your credentials

## Running the Application

### Development
```bash
python app.py
```

### Production
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
aiwr/
├── app.py                 # Flask application factory
├── run.py                 # Production runner
├── config.py              # Configuration settings
├── models.py              # Database models
├── auth.py                # Authentication routes
├── main.py                # Main application routes
├── forms.py               # WTForms forms
├── utils.py               # Utility functions
├── security.py            # Security utilities
├── setup_db.py            # Database setup script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── migrations/           # Database migrations
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgot_password.html
│   │   └── reset_password.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── README.md
```

## Database Models

### User Model
- Email/password authentication
- Google OAuth integration
- Email verification status
- User profile information
- Timestamps and activity tracking

### Token Models
- Password reset tokens with expiration
- Email verification tokens
- Secure token generation with proper validation

## Security Features

### Authentication Security
- Password hashing with bcrypt and salt
- Secure session management
- CSRF protection on all forms
- Rate limiting on sensitive endpoints
- Email verification requirement

### Application Security
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure cookie configuration

### Monitoring & Logging
- Security event logging
- Failed login attempt tracking
- Suspicious activity detection
- Error handling and reporting

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET /auth/login` - Login form
- `POST /auth/login` - Process login
- `GET /auth/register` - Registration form
- `POST /auth/register` - Process registration
- `POST /auth/google-login` - Google OAuth callback
- `GET /auth/logout` - Logout user
- `GET /auth/forgot-password` - Password recovery form
- `POST /auth/forgot-password` - Send recovery email
- `GET /auth/reset-password/<token>` - Reset password form
- `POST /auth/reset-password/<token>` - Process password reset
- `GET /auth/verify-email/<token>` - Email verification

### Main Application
- `GET /dashboard` - User dashboard (requires login)

## Email Templates

The application includes HTML email templates for:
- Email verification
- Password reset
- Welcome messages

All emails are styled and mobile-responsive.

## Deployment

### Environment Variables for Production
```bash
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/writify_db"
```

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

## Testing

### Manual Testing Checklist
- [ ] User registration with email verification
- [ ] Login with email/password
- [ ] Google OAuth login
- [ ] Password recovery flow
- [ ] Session management
- [ ] Form validation
- [ ] Error handling
- [ ] Security headers
- [ ] Rate limiting

### Test User Creation
Run `python setup_db.py` to create a test admin user:
- Email: admin@writify.com
- Password: admin123456

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Verify database exists

2. **Google OAuth Not Working**
   - Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
   - Verify redirect URIs in Google Console
   - Ensure domain is authorized

3. **Emails Not Sending**
   - Check Mailtrap credentials
   - Verify MAIL_* settings in .env
   - Check Mailtrap inbox for test emails

4. **Static Files Not Loading**
   - Using Tailwind CSS via CDN
   - Check internet connection for CDN resources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@writify.com or open an issue on GitHub.