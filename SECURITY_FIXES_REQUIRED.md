# 🔒 CORREÇÕES DE SEGURANÇA OBRIGATÓRIAS

## ❌ **NÃO DEPLOY EM PRODUÇÃO ATÉ CORRIGIR ESTES ITENS:**

### 1. **CRÍTICO: Open Redirect no Login** (auth.py:28-31)
```python
# ANTES (VULNERÁVEL):
next_page = request.args.get('next')
if next_page:
    return redirect(next_page)

# DEPOIS (SEGURO):
next_page = request.args.get('next')
if next_page and next_page.startswith('/') and not next_page.startswith('//'):
    return redirect(next_page)
return redirect(url_for('main.dashboard'))
```

### 2. **CRÍTICO: Rate Limiting em Auth** (auth.py)
```python
from security import rate_limit

@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=5, per_seconds=300)  # 5 tentativas a cada 5 minutos
def login():
    ...

@auth_bp.route('/register', methods=['GET', 'POST'])
@rate_limit(max_requests=3, per_seconds=3600)  # 3 registros por hora
def register():
    ...

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@rate_limit(max_requests=3, per_seconds=3600)
def forgot_password():
    ...

@auth_bp.route('/google-login', methods=['POST'])
@rate_limit(max_requests=10, per_seconds=300)
def google_login():
    ...
```

### 3. **CRÍTICO: Verificação de Email no Google OAuth** (auth.py:112)
```python
# Adicionar ANTES de criar usuário:
if not idinfo.get('email_verified'):
    current_app.logger.warning(f"Unverified Google email attempt: {idinfo.get('email')}")
    flash('Please verify your Google email address first.', 'error')
    return redirect(url_for('auth.login'))
```

### 4. **CRÍTICO: Remover Logs Sensíveis** (stripe_service.py)
```python
# REMOVER ESTAS LINHAS:
# print(f"🔧 StripeService init - API key starts with: {self.stripe_key[:10]}...")
# print(f"🔧 Monthly price ID: {self.MONTHLY_PRICE_ID}")

# SUBSTITUIR POR:
if current_app.debug:
    current_app.logger.debug("Stripe service initialized")
```

### 5. **IMPORTANTE: Rate Limiting no Webhook** (billing_routes.py:209)
```python
@billing_bp.route('/webhook', methods=['POST'])
@rate_limit(max_requests=100, per_seconds=60)
def webhook():
    ...
```

### 6. **IMPORTANTE: Usar Redis para Rate Limiting** (Produção)
```python
# requirements.txt - Adicionar:
redis>=4.0.0

# security.py - Modificar:
import redis
from flask import current_app

redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.from_url(redis_url)
    return redis_client

def rate_limit(max_requests=5, per_seconds=60, key_func=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if key_func:
                key = key_func()
            else:
                key = f"ratelimit:{request.remote_addr}:{request.endpoint}"
            
            try:
                client = get_redis_client()
                current = client.incr(key)
                
                if current == 1:
                    client.expire(key, per_seconds)
                
                if current > max_requests:
                    abort(429)
                    
            except redis.ConnectionError:
                # Fallback to in-memory if Redis unavailable
                current_app.logger.warning("Redis unavailable, rate limiting disabled")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 7. **ADICIONAR: Account Lockout** (models.py)
```python
# Adicionar ao modelo User:
failed_login_attempts = db.Column(db.Integer, default=0)
account_locked_until = db.Column(db.DateTime, nullable=True)

def is_account_locked(self):
    if self.account_locked_until and self.account_locked_until > datetime.utcnow():
        return True
    return False

def increment_failed_login(self):
    self.failed_login_attempts += 1
    if self.failed_login_attempts >= 5:
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
    db.session.commit()

def reset_failed_login(self):
    self.failed_login_attempts = 0
    self.account_locked_until = None
    db.session.commit()
```

```python
# auth.py - Modificar login():
if user.is_account_locked():
    flash('Account temporarily locked. Try again in 15 minutes.', 'error')
    return redirect(url_for('auth.login'))

if user and user.check_password(form.password.data):
    user.reset_failed_login()  # Reset on success
    login_user(user, remember=form.remember_me.data)
    ...
else:
    if user:
        user.increment_failed_login()
    flash('Invalid email or password.', 'error')
```

### 8. **ADICIONAR: Security Headers HSTS** (app.py:145-151)
```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # ADICIONAR HSTS para HTTPS
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # CSP mais restritivo
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://gsi.google.com https://cdn.tailwindcss.com https://js.stripe.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https: https://lh3.googleusercontent.com; "
        "connect-src 'self' https://accounts.google.com https://api.stripe.com; "
        "frame-src https://accounts.google.com https://js.stripe.com https://checkout.stripe.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    return response
```

### 9. **ADICIONAR: Environment Variable Validation** (config.py)
```python
# Adicionar no início de config.py:
required_env_vars = ['SECRET_KEY', 'DATABASE_URL', 'STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET']

for var in required_env_vars:
    if not os.environ.get(var):
        raise ValueError(f"Missing required environment variable: {var}")

# Validar SECRET_KEY não é default
if os.environ.get('SECRET_KEY') == 'dev-secret-key-change-in-production':
    raise ValueError("Cannot use default SECRET_KEY in production!")
```

### 10. **ADICIONAR: Request Size Limit** (app.py)
```python
# Adicionar em create_app():
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
```

---

## 📋 **CHECKLIST PRÉ-PRODUÇÃO**

- [ ] Corrigir Open Redirect (item 1)
- [ ] Adicionar Rate Limiting em /login, /register, /forgot-password (item 2)
- [ ] Verificar email no Google OAuth (item 3)
- [ ] Remover logs sensíveis (item 4)
- [ ] Rate limit no webhook (item 5)
- [ ] Configurar Redis para rate limiting (item 6)
- [ ] Implementar account lockout (item 7)
- [ ] Habilitar HSTS (item 8)
- [ ] Validar variáveis de ambiente (item 9)
- [ ] Limitar tamanho de requests (item 10)
- [ ] Trocar todas chaves Stripe de test para live
- [ ] Configurar HTTPS/SSL
- [ ] Configurar backup automático do database
- [ ] Configurar monitoring (Sentry, DataDog, etc.)
- [ ] Fazer penetration testing

---

## ⏱️ **PRIORIDADES**

1. **Fazer HOJE:** Itens 1, 2, 3, 4 (CRÍTICOS)
2. **Fazer esta semana:** Itens 5, 6, 7, 8, 9, 10
3. **Antes do launch:** Checklist completo
