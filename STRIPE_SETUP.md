# Stripe Integration Setup Guide

Este guia detalha como configurar a integração Stripe para pagamentos no Writify.

## Pré-requisitos

1. Conta no Stripe (https://stripe.com)
2. Aplicação Writify instalada e funcionando
3. Acesso ao banco de dados PostgreSQL

## Configuração do Stripe

### 1. Configurar Produtos e Preços no Stripe Dashboard

1. **Login no Stripe Dashboard**
   - Acesse https://dashboard.stripe.com
   - Certifique-se de estar no modo "Test" durante desenvolvimento

2. **Criar Produtos**
   
   **Produto 1: Writify Monthly**
   - Nome: "Writify Monthly Plan"
   - Descrição: "Monthly subscription to Writify AI writing assistant"
   - Tipo: Service
   
   **Produto 2: Writify Annual**
   - Nome: "Writify Annual Plan" 
   - Descrição: "Annual subscription to Writify AI writing assistant"
   - Tipo: Service

3. **Configurar Preços**
   
   **Para o plano Monthly:**
   - Preço: $27.00 USD
   - Cobrança: Recorrente
   - Intervalo: Mensal
   - **Copie o Price ID** (ex: `price_1A2B3C...`)
   
   **Para o plano Annual:**
   - Preço: $192.00 USD
   - Cobrança: Recorrente
   - Intervalo: Anual
   - **Copie o Price ID** (ex: `price_2X3Y4Z...`)

### 2. Configurar Webhook

1. **Ir para Webhooks** no Stripe Dashboard
   - Desenvolvedores > Webhooks > Add endpoint

2. **Configurar Endpoint**
   - URL: `https://your-domain.com/webhook` (production) ou `https://your-ngrok-url.ngrok.io/webhook` (development)
   - Eventos a escutar:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

3. **Copiar Webhook Secret**
   - Na página do webhook, copie o "Signing secret" (ex: `whsec_...`)

### 3. Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
# Stripe Configuration (IMPORTANTE: Use chaves de teste em desenvolvimento)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs dos produtos criados
STRIPE_MONTHLY_PRICE_ID=price_...
STRIPE_ANNUAL_PRICE_ID=price_...
```

### 4. Executar Migrações

Execute as migrações para criar as tabelas de subscription:

```bash
# Ativar virtual environment
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Executar migrações
flask db upgrade
```

## Testando a Integração

### 1. Desenvolvimento Local

1. **Instalar ngrok** (para webhook testing)
   ```bash
   # Download em https://ngrok.com/
   ngrok http 5000
   ```

2. **Atualizar webhook URL** no Stripe Dashboard com a URL do ngrok

3. **Testar fluxo de pagamento**
   - Ir para `/pricing`
   - Selecionar um plano
   - Usar cartão de teste: `4242 4242 4242 4242`
   - Data: qualquer data futura
   - CVC: qualquer 3 dígitos

### 2. Cartões de Teste

```
# Sucesso
4242 4242 4242 4242

# Pagamento negado
4000 0000 0000 0002

# Falha de autenticação 3D Secure
4000 0000 0000 3220
```

## Monitoramento

### 1. Logs
- Verifique os logs da aplicação para erros de webhook
- Use Stripe Dashboard > Developer > Events para ver eventos processados

### 2. Testing Checklist

- [ ] Usuário consegue se registrar e iniciar trial
- [ ] Dashboard mostra status de trial corretamente
- [ ] Página de pricing carrega sem erros
- [ ] Checkout redirect funciona
- [ ] Webhook processa eventos corretamente
- [ ] Status de subscription é atualizado após pagamento
- [ ] Billing portal funciona
- [ ] Cancelamento funciona

## Produção

### 1. Configuração

1. **Trocar para chaves de produção**
   - No Stripe Dashboard, alternar para "View live data"
   - Substituir todas as chaves test (`pk_test_`, `sk_test_`) pelas live (`pk_live_`, `sk_live_`)

2. **Webhook de Produção**
   - Criar novo webhook endpoint com URL de produção
   - Atualizar `STRIPE_WEBHOOK_SECRET` com o novo secret

3. **SSL Certificate**
   - Certificar que webhook endpoint tem HTTPS válido
   - Stripe requer SSL para webhooks

### 2. Segurança

1. **Variáveis de Ambiente**
   - Nunca commitar chaves de produção no código
   - Usar serviços seguros para environment variables

2. **Rate Limiting**
   - Implementar rate limiting nas APIs de pagamento
   - Stripe tem limites próprios, mas adicionar camada extra

3. **Logs**
   - Não loggar dados sensíveis de cartão
   - Loggar eventos importantes para debugging

## Troubleshooting

### Problemas Comuns

1. **Webhook não funciona**
   - Verificar se URL é acessível publicamente
   - Verificar se STRIPE_WEBHOOK_SECRET está correto
   - Verificar logs da aplicação

2. **Checkout não redireciona**
   - Verificar se STRIPE_PUBLISHABLE_KEY está correto
   - Verificar se Price IDs estão corretos

3. **Status de subscription não atualiza**
   - Verificar se webhook está sendo processado
   - Verificar se eventos estão sendo marcados como processed

### Support

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- Writify Support: support@writify.com

## Schema da Database

As seguintes tabelas foram criadas para suporte de subscription:

### Users (campos adicionados)
- `subscription_status` - Status atual (trial, active, past_due, canceled, incomplete)
- `subscription_plan` - Plano atual (monthly, annual)  
- `stripe_customer_id` - ID do customer no Stripe
- `trial_ends_at` - Fim do trial
- `subscription_ends_at` - Fim da subscription

### Subscriptions
- Detalhes da subscription ativa
- Sincronizada com dados do Stripe

### Payment_Events  
- Auditoria de todos eventos de webhook
- Para debugging e compliance