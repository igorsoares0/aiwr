# Automated Testing Architecture - Writify AI

## 📋 General Information

**Application:** Writify - AI-Powered Writing Assistant  
**Testing Framework:** CodeceptJS  
**Version:** 1.0  
**QA Engineer:** [QA Engineer Name]  
**Date:** [Current Date]

---

## 🎯 Architecture Overview

This documentation defines the complete automated testing architecture for the Writify system, using CodeceptJS as the main framework, following QA best practices for SaaS applications.

### 🚀 Objectives

- **Complete Coverage:** Automate 80%+ of critical test cases
- **Reliability:** Stable and deterministic tests
- **Maintainability:** Clean and reusable code
- **Scalability:** Architecture that grows with the application
- **CI/CD Integration:** Automatic execution in pipelines

---

## 🏗️ Test Project Structure

```
tests/
├── acceptance/                 # Main E2E tests
│   ├── auth/                  # Authentication module
│   │   ├── registration_test.js
│   │   ├── login_test.js
│   │   ├── google_oauth_test.js
│   │   ├── password_recovery_test.js
│   │   └── email_verification_test.js
│   ├── billing/               # Billing module
│   │   ├── trial_management_test.js
│   │   ├── stripe_checkout_test.js
│   │   ├── subscription_management_test.js
│   │   └── billing_portal_test.js
│   ├── ai_features/           # AI features
│   │   ├── text_management_test.js
│   │   ├── ai_assistance_test.js
│   │   └── document_processing_test.js
│   ├── security/              # Security tests
│   │   ├── access_control_test.js
│   │   ├── csrf_protection_test.js
│   │   └── input_validation_test.js
│   └── ui/                    # UI tests
│       ├── responsive_design_test.js
│       ├── navigation_test.js
│       └── user_experience_test.js
├── api/                       # API tests
│   ├── auth_api_test.js
│   ├── billing_api_test.js
│   ├── ai_api_test.js
│   └── document_api_test.js
├── integration/               # Integration tests
│   ├── stripe_integration_test.js
│   ├── anthropic_api_test.js
│   ├── google_oauth_test.js
│   └── email_service_test.js
├── data/                      # Test data
│   ├── users.json            # Test users
│   ├── documents/            # Test files
│   │   ├── sample.pdf
│   │   ├── test_doc.docx
│   │   └── invalid_file.txt
│   └── test_data.js          # Dynamic data
├── pages/                     # Page Object Model
│   ├── base_page.js
│   ├── auth/
│   │   ├── login_page.js
│   │   ├── register_page.js
│   │   └── forgot_password_page.js
│   ├── dashboard/
│   │   ├── dashboard_page.js
│   │   ├── text_editor_page.js
│   │   └── document_manager_page.js
│   ├── billing/
│   │   ├── pricing_page.js
│   │   ├── billing_page.js
│   │   └── checkout_page.js
│   └── common/
│       ├── header_component.js
│       ├── footer_component.js
│       └── notification_component.js
├── helpers/                   # Custom helpers
│   ├── database_helper.js
│   ├── email_helper.js
│   ├── stripe_helper.js
│   ├── ai_mock_helper.js
│   └── file_helper.js
├── utils/                     # Utilities
│   ├── test_data_generator.js
│   ├── database_cleaner.js
│   ├── screenshot_helper.js
│   └── report_generator.js
├── config/                    # Configurations
│   ├── codecept.conf.js      # Main configuration
│   ├── environments/         # Environment configs
│   │   ├── local.conf.js
│   │   ├── staging.conf.js
│   │   └── production.conf.js
│   └── database.conf.js      # Database configuration
├── reports/                   # Generated reports
│   ├── html/
│   ├── junit/
│   └── allure/
├── screenshots/               # Failure screenshots
└── package.json              # Dependencies
```

---

## 🛠️ Technology Stack

### Core Framework
```javascript
{
  "codeceptjs": "^3.5.0",
  "playwright": "^1.40.0",        // Main helper
  "allure-commandline": "^2.24.0", // Reports
  "webdriver": "^8.0.0"           // Backup helper
}
```

### Supporting Libraries
```javascript
{
  "faker": "^6.6.6",             // Data generation
  "moment": "^2.29.4",           // Date manipulation
  "stripe": "^13.11.0",          // Stripe integration
  "nodemailer": "^6.9.7",       // Email verification
  "pg": "^8.11.3",               // PostgreSQL connection
  "axios": "^1.6.0",             // HTTP requests
  "chai": "^4.3.10",             // Advanced assertions
  "sinon": "^17.0.1",            // Mocks and stubs
  "dotenv": "^16.3.1"            // Environment variables
}
```

### Custom Helpers
```javascript
{
  "DatabaseHelper": "helpers/database_helper.js",
  "EmailHelper": "helpers/email_helper.js",
  "StripeHelper": "helpers/stripe_helper.js",
  "AIMockHelper": "helpers/ai_mock_helper.js"
}
```

---

## ⚙️ Main Configuration

### codecept.conf.js
```javascript
const { setHeadlessWhen, setCommonPlugins } = require('@codeceptjs/configure');

setHeadlessWhen(process.env.HEADLESS);
setCommonPlugins();

const config = {
  tests: './acceptance/**/*_test.js',
  output: './reports',
  
  helpers: {
    Playwright: {
      url: process.env.TEST_BASE_URL || 'http://localhost:5000',
      browser: 'chromium',
      show: !process.env.HEADLESS,
      waitForTimeout: 10000,
      waitForAction: 1000,
      windowSize: '1920x1080',
      chromium: {
        args: [
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--no-sandbox',
          '--disable-setuid-sandbox'
        ]
      }
    },
    
    REST: {
      endpoint: process.env.API_BASE_URL || 'http://localhost:5000',
      defaultHeaders: {
        'Content-Type': 'application/json'
      }
    },
    
    DatabaseHelper: {
      require: './helpers/database_helper.js'
    },
    
    EmailHelper: {
      require: './helpers/email_helper.js'
    },
    
    StripeHelper: {
      require: './helpers/stripe_helper.js'
    }
  },
  
  include: {
    I: './pages/base_page.js',
    loginPage: './pages/auth/login_page.js',
    registerPage: './pages/auth/register_page.js',
    dashboardPage: './pages/dashboard/dashboard_page.js',
    pricingPage: './pages/billing/pricing_page.js'
  },
  
  plugins: {
    allure: {
      enabled: true,
      require: '@codeceptjs/allure-legacy'
    },
    
    screenshotOnFail: {
      enabled: true
    },
    
    retryFailedStep: {
      enabled: true,
      retries: 2
    },
    
    wdio: {
      enabled: true,
      services: ['selenium-standalone']
    }
  },
  
  mocha: {
    timeout: 60000,
    reporter: 'spec'
  },
  
  bootstrap: './utils/bootstrap.js',
  teardown: './utils/teardown.js',
  
  hooks: [
    './hooks/database_hooks.js',
    './hooks/screenshot_hooks.js'
  ],
  
  gherkin: {
    features: './features/*.feature',
    steps: ['./step_definitions/*.js']
  }
};

// Environment-specific configurations
if (process.env.TEST_ENV === 'staging') {
  config.helpers.Playwright.url = process.env.STAGING_URL;
} else if (process.env.TEST_ENV === 'production') {
  config.helpers.Playwright.url = process.env.PRODUCTION_URL;
  config.helpers.Playwright.show = false;
}

module.exports = config;
```

---

## 📄 Page Object Model

### Base Page
```javascript
// pages/base_page.js
class BasePage {
  constructor() {
    this.I = actor();
  }
  
  async waitForPageLoad() {
    this.I.waitForElement('body', 10);
    this.I.wait(1); // Wait for JS to load
  }
  
  async takeScreenshot(name) {
    this.I.saveScreenshot(`${name}_${Date.now()}.png`);
  }
  
  async verifyNoJSErrors() {
    const logs = await this.I.grabBrowserLogs();
    const errors = logs.filter(log => log.level === 'SEVERE');
    if (errors.length > 0) {
      throw new Error(`JavaScript errors found: ${JSON.stringify(errors)}`);
    }
  }
  
  async fillFormField(locator, value) {
    this.I.waitForElement(locator, 5);
    this.I.clearField(locator);
    this.I.fillField(locator, value);
  }
  
  async clickAndWait(locator, waitFor = null) {
    this.I.waitForElement(locator, 5);
    this.I.click(locator);
    if (waitFor) {
      this.I.waitForElement(waitFor, 10);
    }
  }
}

module.exports = BasePage;
```

### Login Page Example
```javascript
// pages/auth/login_page.js
const BasePage = require('../base_page');

class LoginPage extends BasePage {
  constructor() {
    super();
    
    // Locators
    this.emailField = '[data-testid="login-email"]';
    this.passwordField = '[data-testid="login-password"]';
    this.rememberMeCheckbox = '[data-testid="remember-me"]';
    this.loginButton = '[data-testid="login-submit"]';
    this.googleLoginButton = '[data-testid="google-login"]';
    this.forgotPasswordLink = '[data-testid="forgot-password"]';
    this.registerLink = '[data-testid="register-link"]';
    this.errorMessage = '[data-testid="error-message"]';
    this.flashMessage = '.flash-message';
  }
  
  async navigate() {
    this.I.amOnPage('/auth/login');
    await this.waitForPageLoad();
  }
  
  async login(email, password, rememberMe = false) {
    await this.fillFormField(this.emailField, email);
    await this.fillFormField(this.passwordField, password);
    
    if (rememberMe) {
      this.I.checkOption(this.rememberMeCheckbox);
    }
    
    await this.clickAndWait(this.loginButton, this.flashMessage);
  }
  
  async loginWithGoogle() {
    await this.clickAndWait(this.googleLoginButton);
    // Google OAuth flow would be handled in specific helper
  }
  
  async verifyLoginError(expectedMessage) {
    this.I.waitForElement(this.errorMessage, 5);
    this.I.see(expectedMessage, this.errorMessage);
  }
  
  async verifySuccessfulLogin() {
    this.I.waitForURL('/dashboard', 10);
    this.I.seeInCurrentUrl('/dashboard');
  }
  
  async goToForgotPassword() {
    await this.clickAndWait(this.forgotPasswordLink);
    this.I.waitForURL('/auth/forgot-password', 5);
  }
  
  async goToRegister() {
    await this.clickAndWait(this.registerLink);
    this.I.waitForURL('/auth/register', 5);
  }
}

module.exports = new LoginPage();
```

---

## 🔧 Custom Helpers

### Database Helper
```javascript
// helpers/database_helper.js
const { Client } = require('pg');
const Helper = require('@codeceptjs/helper');

class DatabaseHelper extends Helper {
  constructor(config) {
    super(config);
    this.client = new Client({
      connectionString: process.env.DATABASE_URL
    });
  }
  
  async _before() {
    await this.client.connect();
  }
  
  async _after() {
    await this.client.end();
  }
  
  async createTestUser(userData = {}) {
    const defaultUser = {
      first_name: 'Test',
      last_name: 'User',
      email: `test${Date.now()}@example.com`,
      password_hash: await this.hashPassword('password123'),
      email_verified: true,
      subscription_status: 'trial',
      trial_ends_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    };
    
    const user = { ...defaultUser, ...userData };
    
    const query = `
      INSERT INTO users (first_name, last_name, email, password_hash, 
                        email_verified, subscription_status, trial_ends_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `;
    
    const result = await this.client.query(query, [
      user.first_name, user.last_name, user.email, user.password_hash,
      user.email_verified, user.subscription_status, user.trial_ends_at
    ]);
    
    return result.rows[0];
  }
  
  async expireUserTrial(userId) {
    const query = `
      UPDATE users 
      SET subscription_status = 'trial_expired', 
          trial_ends_at = NOW() - INTERVAL '1 day'
      WHERE id = $1
    `;
    
    await this.client.query(query, [userId]);
  }
  
  async createTestText(userId, textData = {}) {
    const defaultText = {
      title: 'Test Article',
      content: 'This is test content for the article.',
      user_id: userId
    };
    
    const text = { ...defaultText, ...textData };
    
    const query = `
      INSERT INTO texts (title, content, user_id)
      VALUES ($1, $2, $3)
      RETURNING *
    `;
    
    const result = await this.client.query(query, [
      text.title, text.content, text.user_id
    ]);
    
    return result.rows[0];
  }
  
  async cleanupTestData() {
    // Clean test data in order to respect FKs
    await this.client.query("DELETE FROM payment_events WHERE created_at < NOW() - INTERVAL '1 hour'");
    await this.client.query("DELETE FROM text_documents");
    await this.client.query("DELETE FROM documents WHERE created_at < NOW() - INTERVAL '1 hour'");
    await this.client.query("DELETE FROM texts WHERE created_at < NOW() - INTERVAL '1 hour'");
    await this.client.query("DELETE FROM subscriptions WHERE created_at < NOW() - INTERVAL '1 hour'");
    await this.client.query("DELETE FROM users WHERE email LIKE 'test%@example.com'");
  }
  
  async getUserByEmail(email) {
    const result = await this.client.query('SELECT * FROM users WHERE email = $1', [email]);
    return result.rows[0];
  }
  
  async hashPassword(password) {
    // Implement bcrypt hash here
    const bcrypt = require('bcrypt');
    return await bcrypt.hash(password, 10);
  }
}

module.exports = DatabaseHelper;
```

### Email Helper
```javascript
// helpers/email_helper.js
const nodemailer = require('nodemailer');
const Helper = require('@codeceptjs/helper');

class EmailHelper extends Helper {
  constructor(config) {
    super(config);
    this.emails = [];
  }
  
  async _before() {
    // Configure email service mock or connect to Mailtrap
    this.transporter = nodemailer.createTransporter({
      host: process.env.MAIL_SERVER,
      port: process.env.MAIL_PORT,
      auth: {
        user: process.env.MAIL_USERNAME,
        pass: process.env.MAIL_PASSWORD
      }
    });
  }
  
  async waitForEmail(toEmail, subject, timeout = 30000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      const email = await this.getLatestEmail(toEmail, subject);
      if (email) {
        return email;
      }
      await this.I.wait(2);
    }
    
    throw new Error(`Email not received within ${timeout}ms`);
  }
  
  async getLatestEmail(toEmail, subject) {
    // Implement Mailtrap API search or mock
    // Return found email or null
  }
  
  async extractVerificationToken(emailContent) {
    const tokenMatch = emailContent.match(/verify-email\/([a-zA-Z0-9]+)/);
    return tokenMatch ? tokenMatch[1] : null;
  }
  
  async extractPasswordResetToken(emailContent) {
    const tokenMatch = emailContent.match(/reset-password\/([a-zA-Z0-9]+)/);
    return tokenMatch ? tokenMatch[1] : null;
  }
  
  async clearInbox() {
    // Clear Mailtrap inbox
    this.emails = [];
  }
}

module.exports = EmailHelper;
```

### Stripe Helper
```javascript
// helpers/stripe_helper.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const Helper = require('@codeceptjs/helper');

class StripeHelper extends Helper {
  async createTestCustomer(email) {
    const customer = await stripe.customers.create({
      email: email,
      description: 'Test customer for automated tests'
    });
    
    return customer;
  }
  
  async createTestSubscription(customerId, priceId) {
    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [{ price: priceId }],
      payment_behavior: 'default_incomplete',
      expand: ['latest_invoice.payment_intent'],
    });
    
    return subscription;
  }
  
  async simulateSuccessfulPayment(paymentIntentId) {
    await stripe.paymentIntents.confirm(paymentIntentId, {
      payment_method: 'pm_card_visa'  // Test card
    });
  }
  
  async simulateFailedPayment(paymentIntentId) {
    try {
      await stripe.paymentIntents.confirm(paymentIntentId, {
        payment_method: 'pm_card_chargeDeclined'
      });
    } catch (error) {
      // Expected failure
      return error;
    }
  }
  
  async cancelSubscription(subscriptionId) {
    return await stripe.subscriptions.update(subscriptionId, {
      cancel_at_period_end: true
    });
  }
  
  async cleanupTestData() {
    // Clean test customers and subscriptions
    const customers = await stripe.customers.list({
      email: { contains: '@example.com' },
      limit: 100
    });
    
    for (const customer of customers.data) {
      await stripe.customers.del(customer.id);
    }
  }
}

module.exports = StripeHelper;
```

---

## 🧪 Test Structure

### Authentication Test Example
```javascript
// acceptance/auth/login_test.js
Feature('User Authentication');

Before(async ({ I, DatabaseHelper }) => {
  await DatabaseHelper.cleanupTestData();
});

After(async ({ DatabaseHelper }) => {
  await DatabaseHelper.cleanupTestData();
});

Scenario('User can login with valid credentials', async ({ 
  I, loginPage, dashboardPage, DatabaseHelper 
}) => {
  // Arrange
  const testUser = await DatabaseHelper.createTestUser({
    email: 'validuser@example.com',
    password_hash: await DatabaseHelper.hashPassword('validpassword123')
  });
  
  // Act
  await loginPage.navigate();
  await loginPage.login('validuser@example.com', 'validpassword123');
  
  // Assert
  await loginPage.verifySuccessfulLogin();
  await dashboardPage.verifyUserDashboardLoaded();
  
}).tag('@auth').tag('@smoke');

Scenario('User cannot login with invalid credentials', async ({
  I, loginPage
}) => {
  // Act
  await loginPage.navigate();
  await loginPage.login('invalid@example.com', 'wrongpassword');
  
  // Assert
  await loginPage.verifyLoginError('Invalid email or password.');
  I.seeInCurrentUrl('/auth/login');
  
}).tag('@auth').tag('@security');

Scenario('User can login with Remember Me option', async ({
  I, loginPage, dashboardPage, DatabaseHelper
}) => {
  // Arrange
  const testUser = await DatabaseHelper.createTestUser({
    email: 'rememberuser@example.com'
  });
  
  // Act
  await loginPage.navigate();
  await loginPage.login('rememberuser@example.com', 'password123', true);
  
  // Assert
  await loginPage.verifySuccessfulLogin();
  
  // Simulate browser restart
  I.clearCookie();
  I.amOnPage('/dashboard');
  
  // Should still be logged in
  await dashboardPage.verifyUserDashboardLoaded();
  
}).tag('@auth').tag('@session');
```

### API Test Example
```javascript
// api/auth_api_test.js
Feature('Authentication API');

Scenario('POST /auth/login returns token for valid credentials', async ({
  I, DatabaseHelper
}) => {
  // Arrange
  const testUser = await DatabaseHelper.createTestUser({
    email: 'apitest@example.com'
  });
  
  // Act
  I.sendPostRequest('/auth/login', {
    email: 'apitest@example.com',
    password: 'password123'
  });
  
  // Assert
  I.seeResponseCodeIs(200);
  I.seeResponseContainsKeys(['access_token', 'user']);
  I.seeResponseMatchesJsonType({
    access_token: 'string',
    user: {
      id: 'number',
      email: 'string',
      subscription_status: 'string'
    }
  });
  
}).tag('@api').tag('@auth');

Scenario('POST /api/ai-assist requires authentication', async ({ I }) => {
  // Act
  I.sendPostRequest('/api/ai-assist', {
    title: 'Test Article',
    content: 'Test content'
  });
  
  // Assert
  I.seeResponseCodeIs(401);
  I.seeResponseContainsJson({
    error: 'Authentication required'
  });
  
}).tag('@api').tag('@security');
```

### Integration Test Example
```javascript
// integration/stripe_integration_test.js
Feature('Stripe Integration');

Scenario('Complete checkout flow creates subscription', async ({
  I, loginPage, pricingPage, DatabaseHelper, StripeHelper
}) => {
  // Arrange
  const testUser = await DatabaseHelper.createTestUser({
    email: 'stripetest@example.com'
  });
  
  // Act
  await loginPage.navigate();
  await loginPage.login('stripetest@example.com', 'password123');
  
  await pricingPage.navigate();
  await pricingPage.selectMonthlyPlan();
  
  // Stripe checkout flow
  await pricingPage.fillCheckoutForm({
    cardNumber: '4242424242424242',
    expiry: '12/25',
    cvc: '123',
    name: 'Test User'
  });
  
  await pricingPage.submitPayment();
  
  // Assert
  I.waitForURL('/billing-success', 30);
  
  // Verify database updates
  const updatedUser = await DatabaseHelper.getUserByEmail('stripetest@example.com');
  I.assertEqual(updatedUser.subscription_status, 'active');
  I.assertNotEmpty(updatedUser.stripe_customer_id);
  
}).tag('@integration').tag('@billing').tag('@critical');
```

---

## 📊 Test Data Strategy

### Test Data Generator
```javascript
// utils/test_data_generator.js
const faker = require('faker');

class TestDataGenerator {
  static generateUser(overrides = {}) {
    return {
      first_name: faker.name.firstName(),
      last_name: faker.name.lastName(),
      email: faker.internet.email().toLowerCase(),
      password: 'TestPassword123!',
      ...overrides
    };
  }
  
  static generateText(overrides = {}) {
    return {
      title: faker.lorem.sentence(),
      content: faker.lorem.paragraphs(3),
      ...overrides
    };
  }
  
  static generateDocument(overrides = {}) {
    return {
      filename: `${faker.lorem.word()}.pdf`,
      file_type: 'pdf',
      file_size: faker.datatype.number({ min: 1000, max: 5000000 }),
      ...overrides
    };
  }
  
  static generateCreditCard() {
    return {
      number: '4242424242424242',  // Stripe test card
      expiry: '12/25',
      cvc: '123',
      name: faker.name.findName()
    };
  }
  
  static generateInvalidCreditCard() {
    return {
      number: '4000000000000002',  // Stripe declined card
      expiry: '12/25',
      cvc: '123',
      name: faker.name.findName()
    };
  }
}

module.exports = TestDataGenerator;
```

---

## 🚀 Execution and CI/CD

### NPM Scripts
```json
{
  "scripts": {
    "test": "codeceptjs run --steps",
    "test:headless": "HEADLESS=true codeceptjs run",
    "test:smoke": "codeceptjs run --grep @smoke",
    "test:api": "codeceptjs run api/",
    "test:auth": "codeceptjs run acceptance/auth/",
    "test:billing": "codeceptjs run acceptance/billing/",
    "test:parallel": "codeceptjs run-multiple chrome firefox:headless",
    "test:report": "allure serve reports/allure",
    "test:clean": "rm -rf reports/* screenshots/*"
  }
}
```

### GitHub Actions Workflow
```yaml
# .github/workflows/qa-tests.yml
name: QA Automated Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: writify_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    strategy:
      matrix:
        browser: [chrome, firefox]
        test-suite: [smoke, auth, billing, api]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        npm ci
        npx playwright install
    
    - name: Setup test database
      run: |
        npm run db:migrate:test
        npm run db:seed:test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/writify_test
    
    - name: Run tests
      run: npm run test:${{ matrix.test-suite }}
      env:
        HEADLESS: true
        TEST_ENV: ci
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/writify_test
        STRIPE_SECRET_KEY: ${{ secrets.STRIPE_TEST_SECRET_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_TEST_API_KEY }}
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: test-results-${{ matrix.browser }}-${{ matrix.test-suite }}
        path: |
          reports/
          screenshots/
    
    - name: Generate Allure Report
      run: |
        npm install -g allure-commandline
        allure generate reports/allure -o allure-report --clean
    
    - name: Deploy Allure Report
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: allure-report
        destination_dir: test-reports
```

---

## 📈 Metrics and Reports

### Allure Configuration
```javascript
// Add to codecept.conf.js
plugins: {
  allure: {
    enabled: true,
    require: '@codeceptjs/allure-legacy',
    outputDir: 'reports/allure'
  }
}
```

### Custom Reporter
```javascript
// utils/custom_reporter.js
class CustomReporter {
  constructor() {
    this.results = {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      duration: 0,
      features: {}
    };
  }
  
  onTestStart(test) {
    this.results.total++;
  }
  
  onTestPass(test) {
    this.results.passed++;
    this.updateFeatureStats(test, 'passed');
  }
  
  onTestFail(test, error) {
    this.results.failed++;
    this.updateFeatureStats(test, 'failed');
  }
  
  onTestSkip(test) {
    this.results.skipped++;
    this.updateFeatureStats(test, 'skipped');
  }
  
  updateFeatureStats(test, status) {
    const feature = this.extractFeature(test.title);
    if (!this.results.features[feature]) {
      this.results.features[feature] = { passed: 0, failed: 0, skipped: 0 };
    }
    this.results.features[feature][status]++;
  }
  
  generateReport() {
    const report = {
      summary: this.results,
      timestamp: new Date().toISOString(),
      environment: process.env.TEST_ENV,
      coverage: this.calculateCoverage()
    };
    
    require('fs').writeFileSync(
      'reports/test-summary.json', 
      JSON.stringify(report, null, 2)
    );
  }
  
  calculateCoverage() {
    const totalFeatures = Object.keys(this.results.features).length;
    const coveredFeatures = Object.keys(this.results.features)
      .filter(f => this.results.features[f].passed > 0).length;
    
    return {
      feature_coverage: `${((coveredFeatures / totalFeatures) * 100).toFixed(1)}%`,
      test_success_rate: `${((this.results.passed / this.results.total) * 100).toFixed(1)}%`
    };
  }
}

module.exports = CustomReporter;
```

---

## 🔍 Best Practices

### 1. **Test Structure**
- **AAA Pattern**: Arrange, Act, Assert
- **Page Object Model**: Separate UI logic
- **Data Driven**: Use parameterized data
- **Independent Tests**: Isolated and idempotent tests

### 2. **Naming Convention**
```javascript
// ✅ Good
Scenario('User can register with valid email and password', ...)

// ❌ Bad  
Scenario('Test 1', ...)
```

### 3. **Smart Waits**
```javascript
// ✅ Good
I.waitForElement('[data-testid="submit-button"]', 10);
I.waitForURL('/dashboard', 15);

// ❌ Bad
I.wait(5); // Hard wait
```

### 4. **Error Handling**
```javascript
try {
  await loginPage.login(user.email, user.password);
} catch (error) {
  await I.saveScreenshot('login_failure.png');
  throw error;
}
```

### 5. **Test Data Management**
- Create unique data for each test
- Clean data after execution
- Use factories for data generation
- Separate test data by environment

### 6. **Meaningful Assertions**
```javascript
// ✅ Good
I.see('Registration successful!', '.success-message');
I.assertEqual(user.subscription_status, 'trial');

// ❌ Bad
I.see('Success');
```

---

## 🐛 Debug and Troubleshooting

### Debug Mode
```javascript
// Run with debug
npx codeceptjs run --debug

// Pause execution
I.pause();

// Screenshot on failures
I.saveScreenshot('debug_screenshot.png');
```

### Detailed Logs
```javascript
// codecept.conf.js
helpers: {
  Playwright: {
    // ... other configs
    trace: true,
    video: true,
    keepTraceForPassedTests: false
  }
}
```

### Common Issues
1. **Element not found**: Check selectors and waits
2. **Flaky tests**: Add appropriate waits
3. **Data conflicts**: Improve data cleanup
4. **Performance**: Optimize queries and operations

---

## 📋 Implementation Checklist

### Phase 1: Basic Setup ✅
- [ ] Install CodeceptJS and dependencies
- [ ] Configure folder structure
- [ ] Implement basic Page Objects
- [ ] Create Database and Email helpers
- [ ] Configure Allure reports

### Phase 2: Core Tests ✅
- [ ] Implement authentication tests
- [ ] Create billing/subscription tests
- [ ] Develop AI functionality tests
- [ ] Add API tests
- [ ] Implement security tests

### Phase 3: Optimization ✅
- [ ] Configure parallel execution
- [ ] Implement CI/CD pipeline
- [ ] Optimize test performance
- [ ] Add metrics and dashboard
- [ ] Document troubleshooting

### Phase 4: Maintenance ✅
- [ ] Establish maintenance routine
- [ ] Create code review process
- [ ] Implement failure alerts
- [ ] Train team in best practices
- [ ] Continuous architecture evolution

---

## 📚 Additional Resources

### Documentation
- [CodeceptJS Official Docs](https://codecept.io/)
- [Playwright Documentation](https://playwright.dev/)
- [Allure Reporting](https://docs.qameta.io/allure/)

### Training Materials
- Page Object Model guides
- Test automation best practices
- Test data management strategies
- CI/CD integration guides

### Tools & Extensions
- VSCode CodeceptJS Extension
- Test results dashboard
- Performance monitoring tools
- Error tracking integration

---

**Status:** 🚀 Ready for Implementation  
**Last Update:** [Current Date]  
**Next Review:** [Date + 1 month]

---

*This architecture should be adapted as the application evolves. New patterns and tools should be regularly evaluated to maintain test quality and efficiency.*