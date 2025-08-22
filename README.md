# Writify - AI-Powered Writing Assistant

A complete, secure, and production-ready SaaS application built with Flask, featuring AI-powered writing assistance, subscription management with Stripe, document processing, and comprehensive authentication system.

## 🚀 Features

### ✅ **AI Writing Assistant**
- AI-powered writing suggestions and improvements
- Document upload and processing with Cloudinary
- Interactive text editor with real-time AI assistance
- Context-aware writing recommendations

### ✅ **Subscription & Billing System**
- Stripe integration for payments
- Monthly and annual subscription plans
- Free trial period (7 days for new users, 1 day for Google OAuth)
- Billing portal for subscription management
- Webhook handling for payment events

### ✅ **Secure Authentication System**
- Email/password registration and login
- Google OAuth integration
- Email verification
- Password recovery with secure tokens
- Session management with Flask-Login

### ✅ **Modern UI Design**
- Responsive design with Tailwind CSS
- Clean, professional interface
- Mobile-friendly authentication forms
- Elegant dashboard interface

### ✅ **Security Features**
- Password hashing with bcrypt
- CSRF protection
- Rate limiting
- Security headers (CSP, HSTS, etc.)
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy ORM

### ✅ **Production Ready**
- PostgreSQL database support
- Email integration with Mailtrap for testing
- Error handling and logging
- Database migrations with Flask-Migrate
- Environment-based configuration
- Cloudinary integration for file uploads

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Stripe account (for payments)
- Anthropic API key (for AI features)
- Google Cloud account (for OAuth - optional)
- Cloudinary account (for file uploads - optional)

## 🛠️ Installation Guide

### 1. Clone and Setup Project

```bash
git clone <repository-url>
cd aiwr
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Basic Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/writify_db

# AI Service (Required)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Stripe Configuration (Required for subscriptions)
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Use test keys for development
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_MONTHLY_PRICE_ID=price_...
STRIPE_ANNUAL_PRICE_ID=price_...

# Google OAuth (Optional but recommended)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration (Mailtrap for testing)
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USE_TLS=True
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_DEFAULT_SENDER=noreply@writify.com

# Cloudinary (Optional for file uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 3. Database Setup

#### Option A: Using Migration Scripts (Recommended)

```bash
# Run migrations
python run_migrations.py

# Initialize database with admin user
python init_database.py
```

#### Option B: Manual Setup

```bash
# Create PostgreSQL database
createdb writify_db

# Initialize Flask-Migrate (if needed)
flask db init

# Create and apply migrations
flask db migrate -m "Initial migration with subscription"
flask db upgrade

# Create admin user
python init_database.py
```

### 4. Stripe Configuration

#### 4.1 Setup Products and Prices

1. **Login to Stripe Dashboard**
   - Go to https://dashboard.stripe.com
   - Make sure you're in "Test mode" during development

2. **Create Products**

   **Product 1: Writify Monthly**
   - Name: "Writify Monthly Plan"
   - Description: "Monthly subscription to Writify AI writing assistant"
   - Type: Service

   **Product 2: Writify Annual**
   - Name: "Writify Annual Plan"
   - Description: "Annual subscription to Writify AI writing assistant"
   - Type: Service

3. **Configure Prices**

   **Monthly Plan:**
   - Price: $27.00 USD
   - Billing: Recurring
   - Interval: Monthly
   - **Copy the Price ID** (e.g., `price_1A2B3C...`)

   **Annual Plan:**
   - Price: $192.00 USD
   - Billing: Recurring
   - Interval: Annual
   - **Copy the Price ID** (e.g., `price_2X3Y4Z...`)

#### 4.2 Setup Webhook

1. **Go to Webhooks** in Stripe Dashboard
   - Developers > Webhooks > Add endpoint

2. **Configure Endpoint**
   - URL: `https://your-domain.com/webhook` (production) or use ngrok for development
   - Events to listen for:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

3. **Copy Webhook Secret**
   - Copy the "Signing secret" (e.g., `whsec_...`)

### 5. Google OAuth Configuration (Optional)

#### 5.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Note the **Project ID**

#### 5.2 Enable Google Identity API

1. Go to **APIs & Services** > **Library**
2. Search for "Google Identity Toolkit API"
3. Click **Enable**

#### 5.3 Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** (for external users)
3. Fill required information:
   - **App name**: Writify
   - **User support email**: your-email@gmail.com
   - **Developer contact email**: your-email@gmail.com
4. **Scopes**: Add necessary scopes:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
5. **Test users**: Add your test emails
6. Click **Save and Continue**

#### 5.4 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client ID**
3. Choose **Web application**
4. Configure:
   - **Name**: Writify Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:5000` (development)
     - `https://yourdomain.com` (production)
   - **Authorized redirect URIs**:
     - `http://localhost:5000/auth/google-login` (development)
     - `https://yourdomain.com/auth/google-login` (production)
5. Click **Create**
6. **Copy the Client ID and Client Secret**

### 6. Email Configuration

#### Using Mailtrap (Recommended for development)

1. Sign up at [Mailtrap](https://mailtrap.io)
2. Create an inbox
3. Get SMTP credentials from inbox settings
4. Update `.env` file with credentials

### 7. Cloudinary Configuration (Optional)

1. Sign up at [Cloudinary](https://cloudinary.com)
2. Get your cloud name, API key, and API secret
3. Add to `.env` file

### 8. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🧪 Testing the Setup

### Test User Account

After running `python init_database.py`, you'll have:
- **Email**: admin@writify.com
- **Password**: admin123456

### Testing Checklist

- [ ] App runs without errors (`python app.py`)
- [ ] Home page loads (`http://localhost:5000`)
- [ ] User registration works and starts 7-day trial
- [ ] Dashboard shows trial status
- [ ] Pricing page loads (`/pricing`)
- [ ] Google OAuth login works (if configured)
- [ ] Stripe checkout flow works (use test card: 4242 4242 4242 4242)
- [ ] AI writing assistance works
- [ ] File upload works (if Cloudinary configured)

### Stripe Test Cards

```
# Successful payment
4242 4242 4242 4242

# Payment declined
4000 0000 0000 0002

# 3D Secure authentication failure
4000 0000 0000 3220
```

## 🗂️ Project Structure

```
aiwr/
├── app.py                      # Flask application factory
├── run.py                      # Production runner
├── config.py                   # Configuration settings
├── models.py                   # Database models
├── auth.py                     # Authentication routes
├── main.py                     # Main application routes
├── billing_routes.py           # Stripe billing routes
├── ai_service.py              # AI service integration
├── document_processor.py       # Document processing
├── stripe_service.py          # Stripe service wrapper
├── subscription_middleware.py  # Subscription checking
├── forms.py                   # WTForms forms
├── utils.py                   # Utility functions
├── security.py               # Security utilities
├── setup_db.py               # Database setup script
├── init_database.py          # Database initialization
├── run_migrations.py         # Migration runner
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── migrations/              # Database migrations
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── pricing.html
│   ├── billing.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgot_password.html
│   │   └── reset_password.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
├── static/
│   └── js/
│       └── editor.js         # Text editor functionality
└── README.md
```

## 🗄️ Database Models

### User Model
- Email/password authentication
- Google OAuth integration
- Subscription status and plan
- Trial period management
- Stripe customer ID
- Email verification status
- Profile information

### Subscription Model
- Active subscription details
- Synced with Stripe data
- Plan type and status

### Document Model
- User-uploaded documents
- Cloudinary integration
- Associated with text projects

### Text Model
- User writing projects
- AI assistance history
- Document associations

### Token Models
- Password reset tokens with expiration
- Email verification tokens
- Secure token generation

### Payment Events
- Webhook event audit log
- For debugging and compliance

## 🛡️ Security Features

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

## 🔌 API Endpoints

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
- `GET /dashboard` - User dashboard (requires login + subscription)
- `GET /pricing` - Pricing page
- `POST /api/ai-assist` - AI writing assistance (requires subscription)
- `POST /api/upload-document` - Document upload (requires subscription)
- `POST /api/save-text` - Save text project (requires subscription)

### Billing
- `GET /billing` - Billing management page
- `POST /create-checkout-session` - Create Stripe checkout
- `GET /billing-success` - Success page after payment
- `POST /webhook` - Stripe webhook handler
- `POST /create-portal-session` - Create billing portal session

## 🚀 Deployment

### Environment Variables for Production

```bash
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/writify_db"

# Switch to live Stripe keys
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export STRIPE_SECRET_KEY="sk_live_..."
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

### Production Checklist

1. **Switch to live Stripe keys** (test → live)
2. **Configure webhook** with production URL
3. **SSL certificate** required
4. **Secure environment variables**
5. **Regular database backups**
6. **Domain verification** for Google OAuth
7. **Production email service** (replace Mailtrap)

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Error
**Solution:**
```bash
# Ensure PostgreSQL is running
sudo service postgresql start

# Check DATABASE_URL in .env file
echo $DATABASE_URL

# Verify database exists
psql -l | grep writify
```

#### Column 'subscription_status' does not exist
**Solution:**
```bash
flask db upgrade
python init_database.py
```

#### Migration Error
**Solution (Reset migrations):**
```bash
# Delete migrations folder
rm -rf migrations

# Recreate migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python init_database.py
```

#### Google OAuth Not Working
**Solutions:**
- Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in .env
- Verify redirect URIs in Google Console match exactly
- Ensure domain is authorized
- Check Content Security Policy allows Google domains

#### Emails Not Sending
**Solutions:**
- Check Mailtrap credentials in .env
- Verify `MAIL_*` settings
- Check Mailtrap inbox for test emails
- Ensure firewall allows SMTP connections

#### Stripe Integration Issues
**Solutions:**
- Verify Stripe keys are correct (test vs live)
- Check Price IDs were created and copied correctly
- Ensure webhook endpoint is publicly accessible (use ngrok for local testing)
- Verify webhook secret matches

#### AI Service Not Working
**Solutions:**
- Check `ANTHROPIC_API_KEY` is valid
- Verify API quota/limits
- Check network connectivity
- Review application logs for API errors

#### File Upload Issues
**Solutions:**
- Check Cloudinary credentials
- Verify file size limits
- Ensure proper CSRF tokens
- Check upload permissions

### Development Tools

#### Local Webhook Testing
```bash
# Install ngrok
# Download from https://ngrok.com/

# Expose local server
ngrok http 5000

# Update webhook URL in Stripe Dashboard with ngrok URL
```

#### Database Reset (Development Only)
```bash
# Drop and recreate database
dropdb writify_db
createdb writify_db

# Reset migrations
rm -rf migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python init_database.py
```

### Monitoring

#### Check Application Status
```bash
# View logs
tail -f app.log

# Check database connections
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"

# Test Stripe connectivity
python -c "import stripe; stripe.api_key='sk_test_...'; print(stripe.Account.retrieve())"
```

#### Performance Monitoring
- Monitor database query performance
- Check AI API response times
- Monitor Stripe webhook processing
- Track user subscription conversion rates

## 📞 Support

### Documentation
- **Stripe**: https://stripe.com/docs
- **Google OAuth**: https://developers.google.com/identity/protocols/oauth2
- **Anthropic API**: https://docs.anthropic.com/
- **Flask**: https://flask.palletsprojects.com/
- **Cloudinary**: https://cloudinary.com/documentation

### Getting Help
- **Issues**: Open an issue on GitHub
- **Email Support**: support@writify.com
- **Stripe Support**: https://support.stripe.com

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

**Happy coding! 🚀**