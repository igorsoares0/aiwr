# Configuração do Login com Google OAuth

Este guia explica como configurar o login com Google OAuth 2.0 no aplicativo Writify.

## Como Funciona o Login com Google

O sistema implementa OAuth 2.0 usando a biblioteca Google Identity Services, permitindo que usuários façam login com suas contas Google sem precisar criar uma nova senha.

### Fluxo de Autenticação

1. **Frontend**: Botão "Log in with Google" carrega o SDK do Google
2. **Usuário**: Clica no botão e é redirecionado para o Google
3. **Google**: Usuário autentica e autoriza o app
4. **Callback**: Google retorna um JWT token para o frontend
5. **Backend**: Verifica o token e cria/atualiza o usuário
6. **Login**: Usuário é logado automaticamente no sistema

## Arquivos Envolvidos

### Backend (`auth.py`)
- **`/auth/google-login`**: Endpoint que recebe o token do Google
- **Verificação**: Valida o token JWT usando `google.oauth2.id_token`
- **Criação de usuário**: Cria novo usuário ou vincula conta existente
- **Trial**: Inicia trial de 1 dia automaticamente para novos usuários

### Frontend (`templates/auth/login.html`)
- **Google SDK**: Carrega `https://accounts.google.com/gsi/client`
- **Botão**: Interface para iniciar o login
- **Callback**: Função JavaScript que envia o token para o backend

### Configuração (`config.py`)
- **`GOOGLE_CLIENT_ID`**: ID público da aplicação Google
- **`GOOGLE_CLIENT_SECRET`**: Chave secreta (não usada no frontend)

## Passo a Passo da Configuração

### 1. Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Anote o **Project ID** para referência

### 2. Ativar a Google Identity API

1. No Google Cloud Console, vá em **APIs & Services** > **Library**
2. Procure por "Google Identity" ou "Google+ API"
3. Clique em **Google Identity Toolkit API**
4. Clique em **Enable**

### 3. Configurar OAuth Consent Screen

1. Vá em **APIs & Services** > **OAuth consent screen**
2. Escolha **External** (para usuários externos)
3. Preencha as informações obrigatórias:
   - **App name**: Writify (ou nome do seu app)
   - **User support email**: seu-email@gmail.com
   - **Developer contact email**: seu-email@gmail.com
4. **Scopes**: Adicione os escopos necessários:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
5. **Test users**: Adicione seus emails de teste
6. Clique em **Save and Continue**

### 4. Criar Credenciais OAuth 2.0

1. Vá em **APIs & Services** > **Credentials**
2. Clique em **+ CREATE CREDENTIALS** > **OAuth 2.0 Client ID**
3. Escolha **Web application**
4. Configure:
   - **Name**: Writify Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:5000` (desenvolvimento)
     - `https://seudominio.com` (produção)
   - **Authorized redirect URIs**:
     - `http://localhost:5000/auth/google-login` (desenvolvimento)
     - `https://seudominio.com/auth/google-login` (produção)
5. Clique em **Create**
6. **Copie o Client ID** que será mostrado

### 5. Configurar Variáveis de Ambiente

Edite seu arquivo `.env`:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-1234567890abcdefghijk
```

**Onde encontrar:**
- **Client ID**: Na página de credenciais do Google Cloud Console
- **Client Secret**: Clique no nome da credencial para ver o secret

### 6. Instalar Dependências Python

As dependências já estão no `requirements.txt`:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### 7. Verificar Configuração do CSP

No arquivo `app.py`, certifique-se que o Content Security Policy permite o Google:

```python
response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com"
```

## Testando a Configuração

### 1. Verificar Variáveis de Ambiente

```python
# No terminal Python
import os
print(os.getenv('GOOGLE_CLIENT_ID'))  # Deve mostrar seu Client ID
```

### 2. Testar Login Local

1. Execute o app: `python app.py`
2. Acesse `http://localhost:5000/auth/login`
3. Clique em "Log in with Google"
4. Você deve ser redirecionado para o Google
5. Após autorizar, deve voltar logado ao dashboard

### 3. Verificar Logs

Se der erro, verifique os logs no terminal para mensagens como:
- `Google authentication failed`
- `Invalid Google token`
- `ValueError` (token inválido)

## Problemas Comuns e Soluções

### ❌ "redirect_uri_mismatch"
**Problema**: URL de redirecionamento não autorizada
**Solução**: Verifique se a URL está exatamente igual no Google Cloud Console

### ❌ "invalid_client"
**Problema**: Client ID incorreto ou não encontrado
**Solução**: Verifique se `GOOGLE_CLIENT_ID` está correto no `.env`

### ❌ "Token verification failed"
**Problema**: Token JWT inválido ou expirado
**Solução**: Verifique conexão com internet e configuração do CSP

### ❌ Botão Google não aparece
**Problema**: SDK não carregou ou CSP bloqueando
**Solução**: Verifique console do browser e configuração CSP

## Configuração para Produção

### 1. Domínio Verificado
- Adicione seu domínio nas **Authorized JavaScript origins**
- Use HTTPS obrigatoriamente em produção

### 2. Verificação de Domínio
- No Google Search Console, verifique propriedade do domínio
- Isso pode ser necessário para alguns recursos avançados

### 3. Limites e Quotas
- Google tem limites de requisições por dia
- Para apps grandes, considere solicitar aumento de quota

## Funcionalidades Implementadas

### ✅ Criação Automática de Conta
- Novos usuários são criados automaticamente
- Email já vem verificado (pois vem do Google)
- Trial de 1 dia é iniciado automaticamente

### ✅ Vinculação de Contas
- Se usuário já tem conta com mesmo email, vincula com Google
- Permite login tanto com senha quanto com Google

### ✅ Dados do Perfil
- Nome e sobrenome são extraídos do Google
- Avatar URL é salvo e pode ser usado na interface
- Email sempre vem do Google (confiável)

### ✅ Segurança
- Token JWT é verificado contra certificados do Google
- Verifica se o token foi emitido pelo Google
- Protege contra ataques de token replay

## Arquitetura do Sistema

```
[Frontend] 
    ↓ (clique no botão)
[Google OAuth] 
    ↓ (retorna JWT token)
[JavaScript] 
    ↓ (POST /auth/google-login)
[Flask Backend] 
    ↓ (verifica token)
[Google API] 
    ↓ (token válido)
[Banco de Dados] 
    ↓ (cria/atualiza usuário)
[Login Completo]
```

Este setup proporciona uma experiência de login rápida e segura, reduzindo atrito para novos usuários e aumentando conversões.