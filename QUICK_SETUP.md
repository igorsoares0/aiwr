# 🚀 Quick Setup Guide - Writify com Stripe

## **Passo a Passo Rápido**

### 1. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 2. **Configurar Environment**
```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
# ou
cp .env.example .env    # Linux/Mac

# Editar .env com suas configurações
```

**Mínimo necessário no .env:**
```env
DATABASE_URL=postgresql://username:password@localhost/writify_db
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-key

# Stripe (usar chaves de teste primeiro)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_MONTHLY_PRICE_ID=price_...
STRIPE_ANNUAL_PRICE_ID=price_...
```

### 3. **Setup do Banco de Dados**

**Opção A - Usando setup_db.py (pode dar erro):**
```bash
python setup_db.py
```

**Opção B - Usando Flask-Migrate (RECOMENDADO):**
```bash
# Executar migrações
python run_migrations.py

# Criar usuário admin
python init_database.py
```

**Se precisar resetar migrações:**
```bash
# Deletar pasta migrations
rm -rf migrations  # Linux/Mac
rmdir /s migrations  # Windows

# Recriar migrações
flask db init
flask db migrate -m "Initial migration with subscription"
flask db upgrade
python init_database.py
```

### 4. **Executar Aplicação**
```bash
python app.py
```

## **🔧 Troubleshooting**

### Erro "column users.subscription_status does not exist"
```bash
# Solução:
flask db upgrade
python init_database.py
```

### Erro de migração
```bash
# Reset completo:
1. Deletar pasta migrations
2. flask db init
3. flask db migrate -m "Initial migration"
4. flask db upgrade
5. python init_database.py
```

### Stripe não funciona
```bash
# Verificar:
1. Chaves no .env estão corretas
2. Price IDs foram criados no Stripe Dashboard
3. Webhook está configurado (opcional para testes locais)
```

## **✅ Checklist de Funcionamento**

- [ ] App roda sem erros (`python app.py`)
- [ ] Página inicial carrega (`http://localhost:5000`)
- [ ] Registro funciona e inicia trial de 7 dias
- [ ] Dashboard mostra status do trial
- [ ] Página de pricing carrega (`/pricing`)
- [ ] Admin user existe (admin@writify.com / admin123456)

## **🎯 Para Produção**

1. **Substituir chaves Stripe** (test → live)
2. **Configurar webhook** com URL de produção  
3. **SSL certificate** obrigatório
4. **Environment variables** seguras
5. **Backup do banco** regularmente

## **📞 Suporte**

- **Setup Issues**: `STRIPE_SETUP.md`
- **Database**: `run_migrations.py`
- **General**: `README.md`