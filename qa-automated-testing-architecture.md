# Arquitetura de Testes Automatizados - Writify AI

## 📋 Informações Gerais

**Aplicação:** Writify - AI-Powered Writing Assistant  
**Framework de Testes:** CodeceptJS  
**Versão:** 1.0  
**Responsável QA:** [Nome do QA Engineer]  
**Data:** [Data Atual]

---

## 🎯 Visão Geral da Arquitetura

Esta documentação define a arquitetura completa de testes automatizados para o sistema Writify, utilizando CodeceptJS como framework principal, seguindo as melhores práticas de QA para aplicações SaaS.

### 🚀 Objetivos

- **Cobertura Completa:** Automatizar 80%+ dos casos de teste críticos
- **Confiabilidade:** Testes estáveis e determinísticos
- **Manutenibilidade:** Código limpo e reutilizável
- **Escalabilidade:** Arquitetura que cresce com a aplicação
- **CI/CD Integration:** Execução automática em pipelines

---

## 🏗️ Estrutura do Projeto de Testes

```
tests/
├── acceptance/                 # Testes E2E principais
│   ├── auth/                  # Módulo de autenticação
│   │   ├── registration_test.js
│   │   ├── login_test.js
│   │   ├── google_oauth_test.js
│   │   ├── password_recovery_test.js
│   │   └── email_verification_test.js
│   ├── billing/               # Módulo de cobrança
│   │   ├── trial_management_test.js
│   │   ├── stripe_checkout_test.js
│   │   ├── subscription_management_test.js
│   │   └── billing_portal_test.js
│   ├── ai_features/           # Funcionalidades de IA
│   │   ├── text_management_test.js
│   │   ├── ai_assistance_test.js
│   │   └── document_processing_test.js
│   ├── security/              # Testes de segurança
│   │   ├── access_control_test.js
│   │   ├── csrf_protection_test.js
│   │   └── input_validation_test.js
│   └── ui/                    # Testes de interface
│       ├── responsive_design_test.js
│       ├── navigation_test.js
│       └── user_experience_test.js
├── api/                       # Testes de API
│   ├── auth_api_test.js
│   ├── billing_api_test.js
│   ├── ai_api_test.js
│   └── document_api_test.js
├── integration/               # Testes de integração
│   ├── stripe_integration_test.js
│   ├── anthropic_api_test.js
│   ├── google_oauth_test.js
│   └── email_service_test.js
├── data/                      # Dados de teste
│   ├── users.json            # Usuários de teste
│   ├── documents/            # Arquivos para teste
│   │   ├── sample.pdf
│   │   ├── test_doc.docx
│   │   └── invalid_file.txt
│   └── test_data.js          # Dados dinâmicos
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
├── helpers/                   # Helpers customizados
│   ├── database_helper.js
│   ├── email_helper.js
│   ├── stripe_helper.js
│   ├── ai_mock_helper.js
│   └── file_helper.js
├── utils/                     # Utilitários
│   ├── test_data_generator.js
│   ├── database_cleaner.js
│   ├── screenshot_helper.js
│   └── report_generator.js
├── config/                    # Configurações
│   ├── codecept.conf.js      # Configuração principal
│   ├── environments/         # Configs por ambiente
│   │   ├── local.conf.js
│   │   ├── staging.conf.js
│   │   └── production.conf.js
│   └── database.conf.js      # Configuração do banco
├── reports/                   # Relatórios gerados
│   ├── html/
│   ├── junit/
│   └── allure/
├── screenshots/               # Screenshots de falhas
└── package.json              # Dependências
```

---

## 🛠️ Stack Tecnológica

### Core Framework
```javascript
{
  "codeceptjs": "^3.5.0",
  "playwright": "^1.40.0",        // Helper principal
  "allure-commandline": "^2.24.0", // Relatórios
  "webdriver": "^8.0.0"           // Backup helper
}
```

### Bibliotecas de Apoio
```javascript
{
  "faker": "^6.6.6",             // Geração de dados
  "moment": "^2.29.4",           // Manipulação de datas
  "stripe": "^13.11.0",          // Integração Stripe
  "nodemailer": "^6.9.7",       // Verificação de emails
  "pg": "^8.11.3",               // Conexão PostgreSQL
  "axios": "^1.6.0",             // Requisições HTTP
  "chai": "^4.3.10",             // Assertions avançadas
  "sinon": "^17.0.1",            // Mocks e stubs
  "dotenv": "^16.3.1"            // Variáveis de ambiente
}
```

### Helpers Customizados
```javascript
{
  "DatabaseHelper": "helpers/database_helper.js",
  "EmailHelper": "helpers/email_helper.js",
  "StripeHelper": "helpers/stripe_helper.js",
  "AIMockHelper": "helpers/ai_mock_helper.js"
}
```

---

## ⚙️ Configuração Principal

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

// Configurações por ambiente
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
    this.I.wait(1); // Aguarda JS carregar
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
    // Google OAuth flow seria tratado em helper específico
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

## 🔧 Helpers Customizados

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
    // Limpar dados de teste em ordem para respeitar FKs
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
    // Implementar hash bcrypt aqui
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
    // Configurar mock do serviço de email ou conectar ao Mailtrap
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
    // Implementar busca no Mailtrap API ou mock
    // Retornar email encontrado ou null
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
    // Limpar inbox do Mailtrap
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
    // Limpar customers e subscriptions de teste
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

## 🧪 Estrutura de Testes

### Exemplo de Teste de Autenticação
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

### Exemplo de Teste de API
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

### Exemplo de Teste de Integração
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

## 📊 Estratégia de Dados de Teste

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

## 🚀 Execução e CI/CD

### Scripts NPM
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

## 📈 Métricas e Relatórios

### Configuração do Allure
```javascript
// Adicionar ao codecept.conf.js
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

## 🔍 Boas Práticas

### 1. **Estrutura de Testes**
- **AAA Pattern**: Arrange, Act, Assert
- **Page Object Model**: Separar lógica da UI
- **Data Driven**: Usar dados parametrizados
- **Independent Tests**: Testes isolados e idempotentes

### 2. **Nomenclatura**
```javascript
// ✅ Bom
Scenario('User can register with valid email and password', ...)

// ❌ Ruim  
Scenario('Test 1', ...)
```

### 3. **Waits Inteligentes**
```javascript
// ✅ Bom
I.waitForElement('[data-testid="submit-button"]', 10);
I.waitForURL('/dashboard', 15);

// ❌ Ruim
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
- Criar dados únicos para cada teste
- Limpar dados após execução
- Usar factories para geração de dados
- Separar dados de teste por ambiente

### 6. **Assertions Significativas**
```javascript
// ✅ Bom
I.see('Registration successful!', '.success-message');
I.assertEqual(user.subscription_status, 'trial');

// ❌ Ruim
I.see('Success');
```

---

## 🐛 Debug e Troubleshooting

### Debug Mode
```javascript
// Executar com debug
npx codeceptjs run --debug

// Pausar execução
I.pause();

// Screenshot em falhas
I.saveScreenshot('debug_screenshot.png');
```

### Logs Detalhados
```javascript
// codecept.conf.js
helpers: {
  Playwright: {
    // ... outras configs
    trace: true,
    video: true,
    keepTraceForPassedTests: false
  }
}
```

### Common Issues
1. **Element não encontrado**: Verificar seletores e waits
2. **Flaky tests**: Adicionar waits adequados
3. **Data conflicts**: Melhorar cleanup de dados
4. **Performance**: Otimizar queries e operações

---

## 📋 Checklist de Implementação

### Fase 1: Setup Básico ✅
- [ ] Instalar CodeceptJS e dependências
- [ ] Configurar estrutura de pastas
- [ ] Implementar Page Objects básicos
- [ ] Criar helpers de Database e Email
- [ ] Configurar relatórios Allure

### Fase 2: Testes Core ✅
- [ ] Implementar testes de autenticação
- [ ] Criar testes de billing/subscription
- [ ] Desenvolver testes de funcionalidades IA
- [ ] Adicionar testes de API
- [ ] Implementar testes de segurança

### Fase 3: Otimização ✅
- [ ] Configurar execução paralela
- [ ] Implementar CI/CD pipeline
- [ ] Otimizar performance dos testes
- [ ] Adicionar métricas e dashboard
- [ ] Documentar troubleshooting

### Fase 4: Manutenção ✅
- [ ] Estabelecer rotina de manutenção
- [ ] Criar processo de code review
- [ ] Implementar alertas de falha
- [ ] Treinar equipe em melhores práticas
- [ ] Evolução contínua da arquitetura

---

## 📚 Recursos Adicionais

### Documentação
- [CodeceptJS Official Docs](https://codecept.io/)
- [Playwright Documentation](https://playwright.dev/)
- [Allure Reporting](https://docs.qameta.io/allure/)

### Training Materials
- Guias de Page Object Model
- Boas práticas de test automation
- Estratégias de test data management
- CI/CD integration guides

### Tools & Extensions
- VSCode CodeceptJS Extension
- Test results dashboard
- Performance monitoring tools
- Error tracking integration

---

**Status:** 🚀 Ready for Implementation  
**Última Atualização:** [Data Atual]  
**Próxima Revisão:** [Data + 1 mês]

---

*Esta arquitetura deve ser adaptada conforme a aplicação evolui. Novos padrões e ferramentas devem ser avaliados regularmente para manter a qualidade e eficiência dos testes.*