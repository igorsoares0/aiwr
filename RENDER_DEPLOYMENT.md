# Deploy Writify no Render

## 🚀 Guia Completo de Deploy

### 1. Preparação dos Arquivos

✅ **Arquivos já criados para o deploy:**
- `render.yaml` - Configuração de infraestrutura
- `build.sh` - Script de build com migrações
- `requirements.txt` - Já contém gunicorn

### 2. Configuração no Render

#### 2.1 Criar Conta no Render
1. Acesse [render.com](https://render.com)
2. Faça login com GitHub/GitLab
3. Conecte seu repositório

#### 2.2 Deploy via Blueprint (Recomendado)
1. **New > Blueprint**
2. Conecte o repositório GitHub
3. O Render detectará automaticamente o `render.yaml`
4. Clique em **Apply**

#### 2.3 Deploy Manual (Alternativo)
1. **New > PostgreSQL Database**
   - Nome: `writify-db`
   - Plan: Free
   
2. **New > Web Service**
   - Conectar repositório
   - Runtime: Python
   - Build Command: `./build.sh`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`

### 3. Variáveis de Ambiente Obrigatórias

Configure estas variáveis em **Environment**:

#### 3.1 Básicas (Obrigatórias)
```bash
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
FLASK_ENV=production
DATABASE_URL=postgresql://... # Auto-configurado pelo Render
```

#### 3.2 AI Service (Obrigatório)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-... # Sua chave da Anthropic
```

#### 3.3 Stripe (Obrigatório para pagamentos)
```bash
# IMPORTANTE: Use chaves LIVE para produção
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_MONTHLY_PRICE_ID=price_...
STRIPE_ANNUAL_PRICE_ID=price_...
```

#### 3.4 Google OAuth (Opcional)
```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

#### 3.5 Email (Produção)
```bash
# Para produção, use um serviço real (ex: SendGrid)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

#### 3.6 Cloudinary (Opcional)
```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 4. Configuração do Stripe para Produção

#### 4.1 Atualizar Webhook
1. **Stripe Dashboard > Developers > Webhooks**
2. Criar novo endpoint com URL do Render: `https://your-app.onrender.com/webhook`
3. Eventos necessários:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

#### 4.2 Usar Chaves LIVE
- Trocar todas as chaves de `test` para `live`
- Atualizar Price IDs para os planos de produção

### 5. Configuração Google OAuth

#### 5.1 Atualizar URLs Autorizadas
No Google Cloud Console:
1. **APIs & Services > Credentials**
2. Editar OAuth 2.0 Client
3. **Authorized redirect URIs**:
   - `https://your-app.onrender.com/auth/google-login`

### 6. Domínio Personalizado (Opcional)

1. **Settings > Custom Domains**
2. Adicionar seu domínio
3. Configurar DNS:
   ```
   CNAME www your-app.onrender.com
   ```

### 7. Monitoramento

#### 7.1 Logs
- **Logs** tab no dashboard do Render
- Monitorar erros de startup

#### 7.2 Métricas
- **Metrics** tab para performance
- CPU/Memory usage
- Response times

### 8. Checklist Pós-Deploy

- [ ] App está rodando sem erros
- [ ] Database conectada
- [ ] Página inicial carrega
- [ ] Registro de usuários funciona
- [ ] Login funciona
- [ ] Google OAuth funciona (se configurado)
- [ ] Stripe checkout funciona
- [ ] AI assistant responde
- [ ] Upload de arquivos funciona (se Cloudinary configurado)
- [ ] Emails são enviados
- [ ] Webhook do Stripe funciona

### 9. Troubleshooting

#### 9.1 Erros Comuns

**Build Failed:**
```bash
# Verificar logs de build
# Comum: problemas com psycopg2-binary
```

**Database Connection Error:**
```bash
# Verificar se DATABASE_URL está configurada
# Render configura automaticamente
```

**Environment Variables:**
```bash
# Verificar se todas as variáveis obrigatórias estão configuradas
# SECRET_KEY, ANTHROPIC_API_KEY são essenciais
```

#### 9.2 Debug
```bash
# Ver logs em tempo real
render logs -f your-service-name
```

### 10. Custos

#### Free Tier Inclui:
- ✅ Web Service (750 horas/mês)
- ✅ PostgreSQL (90 dias, depois $7/mês)
- ✅ SSL automático
- ✅ Deploy automático do GitHub

#### Paid Plans:
- **Starter ($7/mês)**: Para apps pequenos
- **Standard ($25/mês)**: Para produção

---

## 🎯 Deploy em 3 Passos

1. **Push para GitHub** com os arquivos criados
2. **Conectar no Render** via Blueprint
3. **Configurar variáveis** de ambiente

**Seu app estará online em ~5 minutos!** 🚀