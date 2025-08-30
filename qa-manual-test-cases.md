# Plano de Testes Manuais - Writify AI Writing Assistant

## 📋 Informações Gerais

**Aplicação:** Writify - AI-Powered Writing Assistant  
**Versão:** 1.0  
**Ferramenta de Gestão:** Qase.io  
**Responsável QA:** [Nome do QA Engineer]  
**Data:** [Data Atual]  

---

## 🎯 Escopo dos Testes

Este documento descreve os casos de teste manuais para o sistema Writify, cobrindo:

- ✅ Sistema de Autenticação (Email/Senha + Google OAuth)
- ✅ Gestão de Usuários e Perfil
- ✅ Sistema de Assinaturas e Billing (Stripe)
- ✅ Funcionalidades de IA para Escrita
- ✅ Gestão de Documentos e Textos
- ✅ Sistema de Trial e Limites de Uso
- ✅ Interface de Usuário e Responsividade
- ✅ Segurança e Validações
- ✅ Tratamento de Erros

---

## 🏗️ Ambiente de Testes

**URLs:**
- **Desenvolvimento:** `http://localhost:5000`
- **Staging:** `[URL_STAGING]`
- **Produção:** `[URL_PRODUCTION]`

**Dados de Teste:**
- **Admin:** admin@writify.com / admin123456
- **Usuário Trial:** trial@test.com / password123
- **Cartão Teste Stripe:** 4242 4242 4242 4242

---

## 📊 Estrutura dos Test Cases

Cada test case segue o padrão:
- **ID:** Identificador único
- **Título:** Descrição concisa do teste
- **Pré-condições:** Estado necessário antes do teste
- **Passos:** Sequência detalhada de ações
- **Resultado Esperado:** Comportamento esperado
- **Critérios de Aceitação:** Condições para aprovação
- **Prioridade:** Alta/Média/Baixa
- **Tags:** Para categorização no Qase.io

---

# 🔐 1. MÓDULO DE AUTENTICAÇÃO

## 1.1 Cadastro de Usuário

### TC001 - Cadastro com Email/Senha Válidos
**Prioridade:** Alta  
**Tags:** authentication, registration, smoke  

**Pré-condições:**
- Aplicação carregada na página inicial
- Email não cadastrado anteriormente

**Passos:**
1. Acessar `/auth/register`
2. Preencher campo "First Name" com "João"
3. Preencher campo "Last Name" com "Silva"
4. Preencher campo "Email" com "joao.silva@test.com"
5. Preencher campo "Password" com "senha123456"
6. Preencher campo "Confirm Password" com "senha123456"
7. Clicar no botão "Sign Up"

**Resultado Esperado:**
- Usuário redirecionado para página de login
- Flash message: "Registration successful! Please check your email to verify your account."
- Email de verificação enviado
- Usuário criado no banco com status trial ativo por 7 dias
- trial_ends_at preenchido com data/hora atual + 7 dias

**Critérios de Aceitação:**
- [ ] Usuário criado na tabela users
- [ ] Password hasheado com bcrypt
- [ ] email_verified = false
- [ ] subscription_status = 'trial'
- [ ] Email de verificação enviado

---

### TC002 - Validação de Email Já Cadastrado
**Prioridade:** Alta  
**Tags:** authentication, registration, validation  

**Pré-condições:**
- Email "teste@test.com" já cadastrado no sistema

**Passos:**
1. Acessar `/auth/register`
2. Preencher todos os campos corretamente
3. Preencher campo "Email" com "teste@test.com"
4. Clicar no botão "Sign Up"

**Resultado Esperado:**
- Erro exibido: "Email already registered. Please use a different email or try logging in."
- Usuário permanece na página de cadastro
- Formulário não é submetido

**Critérios de Aceitação:**
- [ ] Mensagem de erro exibida
- [ ] Nenhum registro duplicado criado
- [ ] Usuário não redirecionado

---

### TC003 - Validação de Senhas Não Coincidentes
**Prioridade:** Alta  
**Tags:** authentication, registration, validation  

**Pré-condições:**
- Aplicação carregada na página de cadastro

**Passos:**
1. Acessar `/auth/register`
2. Preencher campos nome e email corretamente
3. Preencher campo "Password" com "senha123"
4. Preencher campo "Confirm Password" com "senha456"
5. Clicar no botão "Sign Up"

**Resultado Esperado:**
- Erro exibido: "Passwords must match"
- Formulário não submetido
- Campos de senha destacados com erro

**Critérios de Aceitação:**
- [ ] Mensagem de erro exibida
- [ ] Formulário não submetido
- [ ] Campos em estado de erro

---

### TC004 - Validação de Senha Curta
**Prioridade:** Média  
**Tags:** authentication, registration, validation  

**Pré-condições:**
- Aplicação carregada na página de cadastro

**Passos:**
1. Acessar `/auth/register`
2. Preencher campos nome e email corretamente
3. Preencher campo "Password" com "123"
4. Preencher campo "Confirm Password" com "123"
5. Clicar no botão "Sign Up"

**Resultado Esperado:**
- Erro exibido: "Password must be at least 8 characters long"
- Formulário não submetido

**Critérios de Aceitação:**
- [ ] Mensagem de erro exibida
- [ ] Mínimo de 8 caracteres validado
- [ ] Formulário não submetido

---

## 1.2 Login de Usuário

### TC005 - Login com Credenciais Válidas
**Prioridade:** Alta  
**Tags:** authentication, login, smoke  

**Pré-condições:**
- Usuário cadastrado: admin@writify.com / admin123456
- Email verificado (email_verified = true)

**Passos:**
1. Acessar `/auth/login`
2. Preencher campo "Email" com "admin@writify.com"
3. Preencher campo "Password" com "admin123456"
4. Clicar no botão "Log In"

**Resultado Esperado:**
- Usuário redirecionado para `/dashboard`
- Sessão de usuário criada
- Menu de navegação mostra opções logadas

**Critérios de Aceitação:**
- [ ] Redirecionamento para dashboard
- [ ] Sessão ativa
- [ ] UI atualizada para estado logado

---

### TC006 - Login com Email Não Verificado
**Prioridade:** Alta  
**Tags:** authentication, login, email-verification  

**Pré-condições:**
- Usuário cadastrado mas com email_verified = false

**Passos:**
1. Acessar `/auth/login`
2. Preencher credenciais corretas
3. Clicar no botão "Log In"

**Resultado Esperado:**
- Flash message: "Please verify your email address before logging in."
- Usuário permanece na página de login
- Login não realizado

**Critérios de Aceitação:**
- [ ] Mensagem de aviso exibida
- [ ] Login bloqueado
- [ ] Redirecionamento para login

---

### TC007 - Login com Credenciais Inválidas
**Prioridade:** Alta  
**Tags:** authentication, login, security  

**Pré-condições:**
- Aplicação carregada na página de login

**Passos:**
1. Acessar `/auth/login`
2. Preencher campo "Email" com "inexistente@test.com"
3. Preencher campo "Password" com "senhaerrada"
4. Clicar no botão "Log In"

**Resultado Esperado:**
- Flash message: "Invalid email or password."
- Usuário permanece na página de login
- Campos limpos ou mantidos

**Critérios de Aceitação:**
- [ ] Mensagem de erro genérica
- [ ] Login não realizado
- [ ] Não exposição de informações

---

### TC008 - Função "Remember Me"
**Prioridade:** Média  
**Tags:** authentication, login, session  

**Pré-condições:**
- Usuário com credenciais válidas

**Passos:**
1. Acessar `/auth/login`
2. Preencher credenciais corretas
3. Marcar checkbox "Remember me"
4. Clicar no botão "Log In"
5. Fechar navegador
6. Abrir navegador novamente
7. Acessar aplicação

**Resultado Esperado:**
- Usuário permanece logado após fechar/abrir navegador
- Sessão persistida por período estendido

**Critérios de Aceitação:**
- [ ] Sessão persistente ativa
- [ ] Usuário logado automaticamente
- [ ] Cookie de longa duração criado

---

## 1.3 Google OAuth

### TC009 - Login com Google OAuth - Novo Usuário
**Prioridade:** Alta  
**Tags:** authentication, google-oauth, integration  

**Pré-condições:**
- Conta Google válida não cadastrada no sistema
- Google OAuth configurado corretamente

**Passos:**
1. Acessar `/auth/login`
2. Clicar no botão "Continue with Google"
3. Selecionar conta Google na janela popup
4. Autorizar aplicação Writify
5. Aguardar redirecionamento

**Resultado Esperado:**
- Novo usuário criado automaticamente
- email_verified = true
- google_id preenchido
- Trial de 7 dias iniciado
- Redirecionamento para dashboard

**Critérios de Aceitação:**
- [ ] Usuário criado no banco
- [ ] Campos Google preenchidos
- [ ] Trial iniciado automaticamente
- [ ] Login realizado com sucesso

---

### TC010 - Login com Google OAuth - Usuário Existente
**Prioridade:** Alta  
**Tags:** authentication, google-oauth, linking  

**Pré-condições:**
- Usuário já cadastrado com email existente
- Mesmo email usado na conta Google

**Passos:**
1. Acessar `/auth/login`
2. Clicar no botão "Continue with Google"
3. Selecionar conta Google correspondente
4. Autorizar aplicação

**Resultado Esperado:**
- Conta existente vinculada ao Google
- google_id atualizado no registro existente
- avatar_url atualizado
- Login realizado normalmente

**Critérios de Aceitação:**
- [ ] Conta vinculada com sucesso
- [ ] Dados Google atualizados
- [ ] Nenhum usuário duplicado

---

### TC011 - Tratamento de Erro do Google OAuth
**Prioridade:** Média  
**Tags:** authentication, google-oauth, error-handling  

**Pré-condições:**
- Token do Google inválido/expirado

**Passos:**
1. Simular token inválido ou negação de autorização
2. Verificar redirecionamento e mensagens

**Resultado Esperado:**
- Flash message: "Google authentication failed. Please try again."
- Redirecionamento para página de login
- Nenhum usuário criado com dados inválidos

**Critérios de Aceitação:**
- [ ] Tratamento adequado de erros
- [ ] Mensagem informativa
- [ ] Sistema resiliente a falhas

---

## 1.4 Recuperação de Senha

### TC012 - Solicitação de Reset de Senha
**Prioridade:** Alta  
**Tags:** authentication, password-reset, email  

**Pré-condições:**
- Usuário cadastrado: teste@test.com

**Passos:**
1. Acessar `/auth/forgot-password`
2. Preencher campo "Email" com "teste@test.com"
3. Clicar no botão "Send Reset Link"

**Resultado Esperado:**
- Flash message: "If an account with that email exists, a password reset link has been sent."
- Token gerado na tabela password_reset_tokens
- Email enviado com link de reset
- Redirecionamento para página de login

**Critérios de Aceitação:**
- [ ] Token gerado e salvo
- [ ] Email enviado
- [ ] Mensagem genérica exibida
- [ ] Tokens anteriores invalidados

---

### TC013 - Reset de Senha com Token Válido
**Prioridade:** Alta  
**Tags:** authentication, password-reset, token  

**Pré-condições:**
- Token válido gerado no teste anterior

**Passos:**
1. Acessar link do email: `/auth/reset-password/<token>`
2. Preencher campo "New Password" com "novasenha123"
3. Preencher campo "Confirm New Password" com "novasenha123"
4. Clicar no botão "Reset Password"

**Resultado Esperado:**
- Flash message: "Your password has been reset successfully."
- Senha atualizada no banco de dados
- Token marcado como usado
- Redirecionamento para login

**Critérios de Aceitação:**
- [ ] Senha hasheada e atualizada
- [ ] Token invalidado
- [ ] Login possível com nova senha

---

### TC014 - Reset com Token Expirado
**Prioridade:** Média  
**Tags:** authentication, password-reset, security  

**Pré-condições:**
- Token de reset expirado (>1 hora)

**Passos:**
1. Acessar link com token expirado
2. Verificar comportamento

**Resultado Esperado:**
- Flash message: "Invalid or expired reset token."
- Redirecionamento para `/auth/forgot-password`
- Formulário de reset não exibido

**Critérios de Aceitação:**
- [ ] Token expirado rejeitado
- [ ] Mensagem de erro apropriada
- [ ] Segurança mantida

---

## 1.5 Verificação de Email

### TC015 - Verificação de Email com Token Válido
**Prioridade:** Alta  
**Tags:** authentication, email-verification  

**Pré-condições:**
- Usuário cadastrado com email não verificado
- Token de verificação válido

**Passos:**
1. Acessar link do email: `/auth/verify-email/<token>`

**Resultado Esperado:**
- Flash message: "Your email has been verified successfully!"
- email_verified atualizado para true
- Token marcado como usado
- Redirecionamento para login

**Critérios de Aceitação:**
- [ ] Email marcado como verificado
- [ ] Token invalidado
- [ ] Login liberado

---

### TC016 - Logout de Usuário
**Prioridade:** Alta  
**Tags:** authentication, logout, session  

**Pré-condições:**
- Usuário logado no sistema

**Passos:**
1. Clicar no link/botão "Logout"

**Resultado Esperado:**
- Flash message: "You have been logged out."
- Sessão encerrada
- Redirecionamento para página inicial
- Menu atualizado para estado deslogado

**Critérios de Aceitação:**
- [ ] Sessão encerrada
- [ ] Redirecionamento correto
- [ ] UI atualizada

---

# 💳 2. MÓDULO DE BILLING E ASSINATURAS

## 2.1 Sistema de Trial

### TC017 - Início Automático de Trial no Cadastro
**Prioridade:** Alta  
**Tags:** subscription, trial, automatic  

**Pré-condições:**
- Cadastro de novo usuário

**Passos:**
1. Realizar cadastro completo de novo usuário
2. Verificar dados no banco de dados

**Resultado Esperado:**
- subscription_status = 'trial'
- trial_ends_at = data/hora atual + 7 dias
- Acesso liberado às funcionalidades

**Critérios de Aceitação:**
- [ ] Trial iniciado automaticamente
- [ ] Data de expiração correta
- [ ] Status correto no banco

---

### TC018 - Início de Trial - Google OAuth
**Prioridade:** Alta  
**Tags:** subscription, trial, google-oauth  

**Pré-condições:**
- Login com Google OAuth (novo usuário)

**Passos:**
1. Realizar login via Google OAuth
2. Verificar status de trial

**Resultado Esperado:**
- Trial de 7 dias iniciado
- subscription_status = 'trial'
- Acesso às funcionalidades liberado

**Critérios de Aceitação:**
- [ ] Trial iniciado para usuário Google
- [ ] Período correto configurado
- [ ] Funcionalidades disponíveis

---

### TC019 - Expiração Automática de Trial
**Prioridade:** Alta  
**Tags:** subscription, trial, expiration  

**Pré-condições:**
- Usuário com trial prestes a expirar
- Sistema com verificação de trial ativa

**Passos:**
1. Aguardar ou simular data de expiração
2. Tentar acessar funcionalidades protegidas
3. Verificar redirecionamentos

**Resultado Esperado:**
- subscription_status atualizado para 'trial_expired'
- Redirecionamento para página de pricing
- Flash message sobre expiração do trial

**Critérios de Aceitação:**
- [ ] Status atualizado automaticamente
- [ ] Acesso bloqueado após expiração
- [ ] Redirecionamento para pricing

---

## 2.2 Stripe Checkout

### TC020 - Checkout Plano Mensal
**Prioridade:** Alta  
**Tags:** billing, stripe, checkout, monthly  

**Pré-condições:**
- Usuário logado
- Stripe configurado corretamente

**Passos:**
1. Acessar `/pricing`
2. Clicar no botão "Get Monthly Plan" ($27/mês)
3. Verificar redirecionamento para Stripe
4. Preencher dados do cartão: 4242 4242 4242 4242
5. Preencher dados de cobrança
6. Concluir pagamento

**Resultado Esperado:**
- Redirecionamento para Stripe Checkout
- Pagamento processado com sucesso
- Webhook recebido e processado
- subscription_status = 'active'
- Redirecionamento para `/billing-success`

**Critérios de Aceitação:**
- [ ] Checkout Stripe funcional
- [ ] Pagamento processado
- [ ] Webhook processado
- [ ] Status atualizado

---

### TC021 - Checkout Plano Anual
**Prioridade:** Alta  
**Tags:** billing, stripe, checkout, annual  

**Pré-condições:**
- Usuário logado

**Passos:**
1. Acessar `/pricing`
2. Clicar no botão "Get Annual Plan" ($192/ano)
3. Completar checkout no Stripe

**Resultado Esperado:**
- Checkout para plano anual
- Desconto aplicado corretamente
- Subscription criada com período anual

**Critérios de Aceitação:**
- [ ] Preço anual correto
- [ ] Período de cobrança anual
- [ ] Desconto aplicado

---

### TC022 - Cartão Recusado
**Prioridade:** Média  
**Tags:** billing, stripe, error-handling  

**Pré-condições:**
- Usuário no processo de checkout

**Passos:**
1. Iniciar processo de checkout
2. Usar cartão teste recusado: 4000 0000 0000 0002
3. Tentar finalizar pagamento

**Resultado Esperado:**
- Erro exibido no Stripe
- Usuário permanece no checkout
- Nenhuma subscription criada
- Status do usuário inalterado

**Critérios de Aceitação:**
- [ ] Erro tratado adequadamente
- [ ] Nenhuma cobrança processada
- [ ] Usuario pode tentar novamente

---

## 2.3 Gerenciamento de Assinatura

### TC023 - Visualização de Status da Assinatura
**Prioridade:** Alta  
**Tags:** billing, subscription, status  

**Pré-condições:**
- Usuário com assinatura ativa

**Passos:**
1. Fazer login
2. Acessar `/billing`
3. Verificar informações exibidas

**Resultado Esperado:**
- Status da assinatura exibido
- Plano atual mostrado
- Data de renovação visível
- Opções de gerenciamento disponíveis

**Critérios de Aceitação:**
- [ ] Informações precisas
- [ ] UI clara e informativa
- [ ] Dados sincronizados com Stripe

---

### TC024 - Cancelamento de Assinatura
**Prioridade:** Alta  
**Tags:** billing, subscription, cancellation  

**Pré-condições:**
- Usuário com assinatura ativa

**Passos:**
1. Acessar `/billing`
2. Clicar em botão de cancelamento
3. Confirmar cancelamento

**Resultado Esperado:**
- Assinatura cancelada no fim do período
- Status atualizado para indicar cancelamento
- Flash message confirmando ação
- Acesso mantido até fim do período

**Critérios de Aceitação:**
- [ ] Cancelamento no fim do período
- [ ] Status atualizado
- [ ] Acesso mantido

---

### TC025 - Reativação de Assinatura Cancelada
**Prioridade:** Média  
**Tags:** billing, subscription, reactivation  

**Pré-condições:**
- Assinatura cancelada mas ainda no período pago

**Passos:**
1. Acessar `/billing`
2. Clicar em botão de reativação
3. Confirmar reativação

**Resultado Esperado:**
- Assinatura reativada
- Cancelamento removido
- Status atualizado
- Cobrança automática reestabelecida

**Critérios de Aceitação:**
- [ ] Assinatura reativada
- [ ] Status corrigido
- [ ] Cobrança reestabelecida

---

### TC026 - Portal de Billing do Stripe
**Prioridade:** Média  
**Tags:** billing, stripe, portal  

**Pré-condições:**
- Usuário com stripe_customer_id

**Passos:**
1. Acessar `/billing`
2. Clicar em "Manage Billing"
3. Verificar redirecionamento para Stripe Portal

**Resultado Esperado:**
- Redirecionamento para portal do Stripe
- Opções de gerenciamento disponíveis
- Histórico de pagamentos visível

**Critérios de Aceitação:**
- [ ] Portal acessível
- [ ] Opções funcionais
- [ ] Dados corretos

---

## 2.4 Webhooks do Stripe

### TC027 - Webhook - Checkout Completado
**Prioridade:** Alta  
**Tags:** billing, webhook, integration  

**Pré-condições:**
- Pagamento processado com sucesso no Stripe

**Passos:**
1. Simular ou aguardar webhook `checkout.session.completed`
2. Verificar processamento na aplicação

**Resultado Esperado:**
- Evento registrado na tabela payment_events
- Usuário atualizado com subscription ativa
- stripe_customer_id preenchido
- Subscription criada na tabela subscriptions

**Critérios de Aceitação:**
- [ ] Webhook processado
- [ ] Dados atualizados corretamente
- [ ] Log do evento salvo

---

### TC028 - Webhook - Subscription Updated
**Prioridade:** Alta  
**Tags:** billing, webhook, subscription  

**Pré-condições:**
- Subscription ativa que sofre alteração

**Passos:**
1. Alterar subscription via Stripe Dashboard
2. Verificar processamento do webhook

**Resultado Esperado:**
- Dados locais sincronizados com Stripe
- Status atualizado conforme mudança
- Evento processado e marcado

**Critérios de Aceitação:**
- [ ] Sincronização automática
- [ ] Status correto
- [ ] Webhook processado

---

### TC029 - Webhook - Payment Failed
**Prioridade:** Alta  
**Tags:** billing, webhook, payment-failure  

**Pré-condições:**
- Subscription com falha de pagamento

**Passos:**
1. Simular falha de pagamento no Stripe
2. Verificar processamento do webhook

**Resultado Esperado:**
- Status atualizado para 'past_due'
- Usuário notificado sobre falha
- Acesso mantido por período de graça

**Critérios de Aceitação:**
- [ ] Status atualizado
- [ ] Usuário informado
- [ ] Período de graça ativo

---

# 🤖 3. MÓDULO DE IA E FUNCIONALIDADES PRINCIPAIS

## 3.1 Dashboard

### TC030 - Acesso ao Dashboard - Usuário com Trial Ativo
**Prioridade:** Alta  
**Tags:** dashboard, trial, access  

**Pré-condições:**
- Usuário logado com trial ativo

**Passos:**
1. Fazer login
2. Verificar redirecionamento automático para dashboard
3. Verificar elementos da página

**Resultado Esperado:**
- Acesso permitido ao dashboard
- Informações de trial exibidas
- Lista de textos e documentos visível
- Editor de texto disponível

**Critérios de Aceitação:**
- [ ] Acesso liberado
- [ ] Status de trial visível
- [ ] Funcionalidades disponíveis

---

### TC031 - Acesso ao Dashboard - Trial Expirado
**Prioridade:** Alta  
**Tags:** dashboard, trial, expiration  

**Pré-condições:**
- Usuário com trial expirado

**Passos:**
1. Tentar acessar `/dashboard`

**Resultado Esperado:**
- Redirecionamento para `/pricing`
- Flash message sobre trial expirado
- Acesso negado ao dashboard

**Critérios de Aceitação:**
- [ ] Acesso bloqueado
- [ ] Redirecionamento correto
- [ ] Mensagem informativa

---

### TC032 - Dashboard - Usuário com Subscription Ativa
**Prioridade:** Alta  
**Tags:** dashboard, subscription, access  

**Pré-condições:**
- Usuário com subscription ativa

**Passos:**
1. Acessar dashboard
2. Verificar status exibido

**Resultado Esperado:**
- Acesso total liberado
- Informações de subscription visíveis
- Todas as funcionalidades disponíveis
- Sem limitações de uso

**Critérios de Aceitação:**
- [ ] Acesso total
- [ ] Status correto
- [ ] Funcionalidades completas

---

## 3.2 Gestão de Textos

### TC033 - Criação de Novo Texto
**Prioridade:** Alta  
**Tags:** text-management, creation, api  

**Pré-condições:**
- Usuário logado com acesso válido

**Passos:**
1. Acessar dashboard
2. Clicar em "New Text" ou similar
3. Preencher título: "Meu Primeiro Artigo"
4. Preencher conteúdo inicial
5. Salvar texto

**Resultado Esperado:**
- Texto criado na tabela texts
- Redirecionamento ou atualização da lista
- Texto disponível para edição
- Timestamps created_at e updated_at preenchidos

**Critérios de Aceitação:**
- [ ] Texto salvo no banco
- [ ] Associado ao usuário correto
- [ ] Metadados corretos

---

### TC034 - Edição de Texto Existente
**Prioridade:** Alta  
**Tags:** text-management, editing  

**Pré-condições:**
- Usuário com texto já criado

**Passos:**
1. Acessar dashboard
2. Selecionar texto existente
3. Modificar título e conteúdo
4. Salvar alterações

**Resultado Esperado:**
- Alterações persistidas no banco
- updated_at atualizado
- Versão anterior substituída
- Interface atualizada

**Critérios de Aceitação:**
- [ ] Alterações salvas
- [ ] Timestamp atualizado
- [ ] Interface consistente

---

### TC035 - Listagem de Textos do Usuário
**Prioridade:** Alta  
**Tags:** text-management, listing  

**Pré-condições:**
- Usuário com múltiplos textos criados

**Passos:**
1. Acessar dashboard
2. Verificar lista de textos

**Resultado Esperado:**
- Todos os textos do usuário listados
- Ordenação por data de atualização (mais recentes primeiro)
- Informações básicas exibidas (título, data)
- Opções de ação disponíveis (editar, excluir)

**Critérios de Aceitação:**
- [ ] Lista completa e correta
- [ ] Ordenação adequada
- [ ] Apenas textos do usuário

---

### TC036 - Exclusão de Texto
**Prioridade:** Média  
**Tags:** text-management, deletion  

**Pré-condições:**
- Usuário com texto criado

**Passos:**
1. Selecionar texto para exclusão
2. Confirmar exclusão
3. Verificar remoção

**Resultado Esperado:**
- Texto removido da tabela texts
- Lista atualizada sem o item
- Confirmação de exclusão
- Associações com documentos removidas

**Critérios de Aceitação:**
- [ ] Texto removido permanentemente
- [ ] Lista atualizada
- [ ] Relacionamentos limpos

---

## 3.3 Sistema de IA para Escrita

### TC037 - Solicitação de Sugestões de IA
**Prioridade:** Alta  
**Tags:** ai-assistance, suggestions, api  

**Pré-condições:**
- Usuário com acesso válido
- Anthropic API configurada

**Passos:**
1. Criar ou editar texto
2. Preencher título: "Como fazer um bolo"
3. Preencher conteúdo parcial: "Ingredientes necessários:"
4. Clicar em botão de assistência IA
5. Aguardar resposta

**Resultado Esperado:**
- Requisição enviada para `/api/ai-assist`
- Resposta da IA recebida
- Sugestões exibidas na interface
- Opção de aceitar/rejeitar sugestões

**Critérios de Aceitação:**
- [ ] API respondendo corretamente
- [ ] Sugestões relevantes
- [ ] Interface responsiva

---

### TC038 - IA com Contexto de Documento
**Prioridade:** Alta  
**Tags:** ai-assistance, document-context  

**Pré-condições:**
- Usuário com documento anexado a texto
- Texto com documento associado

**Passos:**
1. Criar texto e associar documento
2. Solicitar sugestões de IA
3. Verificar se contexto do documento é usado

**Resultado Esperado:**
- IA utiliza conteúdo do documento como contexto
- Sugestões mais relevantes e específicas
- Referência ao documento nas sugestões

**Critérios de Aceitação:**
- [ ] Contexto do documento usado
- [ ] Qualidade das sugestões melhorada
- [ ] Integração funcional

---

### TC039 - Tratamento de Erro da API de IA
**Prioridade:** Média  
**Tags:** ai-assistance, error-handling  

**Pré-condições:**
- API da Anthropic indisponível ou com erro

**Passos:**
1. Simular erro na API
2. Tentar solicitar sugestões
3. Verificar tratamento do erro

**Resultado Esperado:**
- Mensagem de erro amigável
- Interface não quebra
- Usuário pode tentar novamente
- Error: "Failed to generate suggestions"

**Critérios de Aceitação:**
- [ ] Erro tratado adequadamente
- [ ] Interface estável
- [ ] Retry disponível

---

### TC040 - Validação de Campos Obrigatórios - IA
**Prioridade:** Média  
**Tags:** ai-assistance, validation  

**Pré-condições:**
- Usuário logado

**Passos:**
1. Tentar solicitar IA sem título
2. Verificar validação

**Resultado Esperado:**
- Erro retornado: "Title is required"
- Status 400
- Solicitação não processada

**Critérios de Aceitação:**
- [ ] Validação funcionando
- [ ] Erro apropriado
- [ ] API protegida

---

## 3.4 Gestão de Documentos

### TC041 - Upload de Documento PDF
**Prioridade:** Alta  
**Tags:** document-management, upload, pdf  

**Pré-condições:**
- Usuário com acesso válido
- Arquivo PDF válido disponível

**Passos:**
1. Acessar funcionalidade de upload
2. Selecionar arquivo PDF
3. Fazer upload

**Resultado Esperado:**
- Arquivo enviado com sucesso
- Texto extraído do PDF
- Documento salvo na tabela documents
- Arquivo armazenado (Cloudinary ou local)
- Metadados corretos preenchidos

**Critérios de Aceitação:**
- [ ] Upload bem-sucedido
- [ ] Texto extraído
- [ ] Metadados corretos

---

### TC042 - Upload de Documento DOCX
**Prioridade:** Alta  
**Tags:** document-management, upload, docx  

**Pré-condições:**
- Usuário com acesso válido
- Arquivo DOCX válido

**Passos:**
1. Fazer upload de arquivo .docx
2. Verificar processamento

**Resultado Esperado:**
- Arquivo DOCX processado
- Texto extraído corretamente
- Documento salvo com tipo 'docx'

**Critérios de Aceitação:**
- [ ] DOCX suportado
- [ ] Extração de texto funcional
- [ ] Tipo identificado corretamente

---

### TC043 - Upload de Arquivo Inválido
**Prioridade:** Média  
**Tags:** document-management, upload, validation  

**Pré-condições:**
- Usuário logado

**Passos:**
1. Tentar fazer upload de arquivo .txt ou .jpg
2. Verificar tratamento

**Resultado Esperado:**
- Upload rejeitado
- Mensagem de erro apropriada
- Nenhum documento criado
- Tipos suportados informados

**Critérios de Aceitação:**
- [ ] Validação de tipo funcional
- [ ] Erro informativo
- [ ] Segurança mantida

---

### TC044 - Exclusão de Documento
**Prioridade:** Média  
**Tags:** document-management, deletion  

**Pré-condições:**
- Usuário com documento já enviado

**Passos:**
1. Selecionar documento para exclusão
2. Confirmar exclusão
3. Verificar remoção

**Resultado Esperado:**
- Documento removido do banco
- Arquivo removido do armazenamento
- Lista atualizada
- Associações com textos removidas

**Critérios de Aceitação:**
- [ ] Documento removido completamente
- [ ] Arquivo físico removido
- [ ] Relacionamentos limpos

---

### TC045 - Associação Documento-Texto
**Prioridade:** Alta  
**Tags:** document-management, text-association  

**Pré-condições:**
- Usuário com documento e texto criados

**Passos:**
1. Acessar funcionalidade de associação
2. Vincular documento específico a texto específico
3. Verificar associação

**Resultado Esperado:**
- Relacionamento criado na tabela text_documents
- Documento disponível como contexto para IA
- Interface mostra associação
- Histórico de associação mantido

**Critérios de Aceitação:**
- [ ] Associação criada
- [ ] Contexto disponível
- [ ] Interface atualizada

---

### TC046 - Desassociação Documento-Texto
**Prioridade:** Média  
**Tags:** document-management, text-disassociation  

**Pré-condições:**
- Documento associado a texto

**Passos:**
1. Remover associação entre documento e texto
2. Verificar remoção

**Resultado Esperado:**
- Relacionamento removido
- Documento não mais disponível como contexto
- Documento permanece disponível para outras associações

**Critérios de Aceitação:**
- [ ] Associação removida
- [ ] Documento preservado
- [ ] Contexto atualizado

---

### TC047 - Listagem de Documentos Disponíveis
**Prioridade:** Média  
**Tags:** document-management, listing  

**Pré-condições:**
- Usuário com múltiplos documentos

**Passos:**
1. Acessar lista de documentos disponíveis para associação
2. Verificar filtros

**Resultado Esperado:**
- Lista de documentos não associados ao texto atual
- Informações relevantes exibidas
- Opções de ação disponíveis

**Critérios de Aceitação:**
- [ ] Lista filtrada corretamente
- [ ] Informações precisas
- [ ] Interface funcional

---

# 🛡️ 4. MÓDULO DE SEGURANÇA E MIDDLEWARE

## 4.1 Controle de Acesso

### TC048 - Middleware de Subscription - Trial Ativo
**Prioridade:** Alta  
**Tags:** security, middleware, trial  

**Pré-condições:**
- Usuário com trial ativo

**Passos:**
1. Tentar acessar rotas protegidas:
   - `/dashboard`
   - `/api/ai-assist`
   - `/api/upload`

**Resultado Esperado:**
- Acesso permitido a todas as rotas
- Funcionalidades disponíveis
- Middleware passa validação

**Critérios de Aceitação:**
- [ ] Acesso liberado
- [ ] Middleware funcionando
- [ ] Validação correta

---

### TC049 - Middleware de Subscription - Trial Expirado
**Prioridade:** Alta  
**Tags:** security, middleware, expiration  

**Pré-condições:**
- Usuário com trial expirado

**Passos:**
1. Tentar acessar rotas protegidas
2. Verificar bloqueios e redirecionamentos

**Resultado Esperado:**
- Redirecionamento para `/pricing`
- Flash message sobre expiração
- APIs retornam 403 com contexto adequado

**Critérios de Aceitação:**
- [ ] Acesso bloqueado corretamente
- [ ] Redirecionamentos adequados
- [ ] APIs protegidas

---

### TC050 - Middleware de API - Usuário Não Autenticado
**Prioridade:** Alta  
**Tags:** security, middleware, api  

**Pré-condições:**
- Usuário não logado

**Passos:**
1. Tentar acessar APIs diretamente:
   - `POST /api/ai-assist`
   - `POST /api/upload`
   - `POST /api/texts`

**Resultado Esperado:**
- Status 401: "Authentication required"
- Nenhuma operação executada
- Sistema protegido

**Critérios de Aceitação:**
- [ ] APIs protegidas
- [ ] Autenticação obrigatória
- [ ] Erros apropriados

---

### TC051 - Verificação Automática de Trial
**Prioridade:** Alta  
**Tags:** security, trial, automatic-check  

**Pré-condições:**
- Sistema em funcionamento
- Usuário com trial prestes a expirar

**Passos:**
1. Simular passagem do tempo
2. Verificar atualização automática
3. Testar acesso após expiração

**Resultado Esperado:**
- Status automaticamente atualizado para 'trial_expired'
- Acesso bloqueado imediatamente
- Middleware funcionando corretamente

**Critérios de Aceitação:**
- [ ] Atualização automática
- [ ] Bloqueio imediato
- [ ] Sistema responsivo

---

## 4.2 Validação e Sanitização

### TC052 - CSRF Protection
**Prioridade:** Alta  
**Tags:** security, csrf, forms  

**Pré-condições:**
- Formulários da aplicação

**Passos:**
1. Tentar submeter formulários sem token CSRF
2. Verificar proteção

**Resultado Esperado:**
- Formulários rejeitados sem token
- Token CSRF presente em todos os forms
- Proteção ativa contra ataques CSRF

**Critérios de Aceitação:**
- [ ] CSRF tokens obrigatórios
- [ ] Submissão bloqueada sem token
- [ ] Proteção efetiva

---

### TC053 - Validação de Email
**Prioridade:** Média  
**Tags:** security, validation, email  

**Pré-condições:**
- Formulários com campos de email

**Passos:**
1. Tentar cadastro/login com emails inválidos:
   - "email_inválido"
   - "test@"
   - "@domain.com"

**Resultado Esperado:**
- Emails inválidos rejeitados
- Mensagens de erro apropriadas
- Validação tanto no frontend quanto backend

**Critérios de Aceitação:**
- [ ] Validação de formato
- [ ] Mensagens de erro
- [ ] Proteção em camadas

---

### TC054 - Sanitização de Inputs
**Prioridade:** Alta  
**Tags:** security, sanitization, xss  

**Pré-condições:**
- Campos de entrada de texto

**Passos:**
1. Tentar inserir scripts maliciosos:
   - `<script>alert('xss')</script>`
   - `javascript:alert('xss')`
   - Códigos HTML maliciosos

**Resultado Esperado:**
- Scripts removidos ou escapados
- Nenhum código malicioso executado
- Conteúdo seguro armazenado

**Critérios de Aceitação:**
- [ ] XSS prevenido
- [ ] Sanitização efetiva
- [ ] Conteúdo seguro

---

## 4.3 Headers de Segurança

### TC055 - Security Headers
**Prioridade:** Média  
**Tags:** security, headers, browser  

**Pré-condições:**
- Aplicação rodando

**Passos:**
1. Inspecionar headers de resposta HTTP
2. Verificar presença de headers de segurança

**Resultado Esperado:**
- Headers presentes:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Content-Security-Policy`

**Critérios de Aceitação:**
- [ ] Headers de segurança presentes
- [ ] Configurações apropriadas
- [ ] Proteção contra ataques

---

### TC056 - Content Security Policy
**Prioridade:** Média  
**Tags:** security, csp, headers  

**Pré-condições:**
- CSP configurado na aplicação

**Passos:**
1. Verificar CSP header
2. Testar carregamento de recursos

**Resultado Esperado:**
- CSP permite apenas origens confiáveis
- Google APIs permitidas
- Stripe checkout permitido
- Scripts maliciosos bloqueados

**Critérios de Aceitação:**
- [ ] CSP configurado
- [ ] Origens confiáveis permitidas
- [ ] Recursos maliciosos bloqueados

---

# 🚨 5. MÓDULO DE TRATAMENTO DE ERROS

## 5.1 Páginas de Erro

### TC057 - Página 404 - Recurso Não Encontrado
**Prioridade:** Média  
**Tags:** error-handling, 404, ui  

**Pré-condições:**
- Aplicação rodando

**Passos:**
1. Acessar URL inexistente: `/pagina-inexistente`
2. Verificar resposta

**Resultado Esperado:**
- Status HTTP 404
- Página de erro personalizada exibida
- Link para voltar à página inicial
- Design consistente com aplicação

**Critérios de Aceitação:**
- [ ] Status 404 correto
- [ ] Página personalizada
- [ ] Navegação disponível

---

### TC058 - Página 500 - Erro Interno
**Prioridade:** Média  
**Tags:** error-handling, 500, ui  

**Pré-condições:**
- Erro interno simulado

**Passos:**
1. Simular erro interno da aplicação
2. Verificar tratamento

**Resultado Esperado:**
- Status HTTP 500
- Página de erro genérica
- Nenhuma informação sensível exposta
- Rollback de transação realizado

**Critérios de Aceitação:**
- [ ] Status 500 correto
- [ ] Informações não expostas
- [ ] Sistema estável

---

### TC059 - Tratamento de Erro de Banco de Dados
**Prioridade:** Alta  
**Tags:** error-handling, database, resilience  

**Pré-condições:**
- Conexão com banco simuladamente instável

**Passos:**
1. Simular erro de conexão com banco
2. Tentar operações que requerem banco
3. Verificar tratamento

**Resultado Esperado:**
- Erro tratado graciosamente
- Usuário informado adequadamente
- Sistema não quebra
- Rollback automático executado

**Critérios de Aceitação:**
- [ ] Erro tratado
- [ ] Sistema estável
- [ ] Rollback funcionando

---

## 5.2 Validação de APIs

### TC060 - API Error - Missing Parameters
**Prioridade:** Média  
**Tags:** error-handling, api, validation  

**Pré-condições:**
- APIs da aplicação

**Passos:**
1. Chamar APIs sem parâmetros obrigatórios
2. Verificar respostas de erro

**Resultado Esperado:**
- Status apropriado (400, 422)
- Mensagens de erro descritivas
- JSON bem formatado
- Nenhuma operação executada

**Critérios de Aceitação:**
- [ ] Status codes corretos
- [ ] Mensagens descritivas
- [ ] APIs protegidas

---

### TC061 - API Error - Invalid Data Types
**Prioridade:** Média  
**Tags:** error-handling, api, data-types  

**Pré-condições:**
- APIs que esperam tipos específicos

**Passos:**
1. Enviar dados com tipos inválidos
2. Verificar validação

**Resultado Esperado:**
- Dados inválidos rejeitados
- Erros de tipo reportados
- Sistema permanece estável

**Critérios de Aceitação:**
- [ ] Validação de tipos
- [ ] Erros informativos
- [ ] Sistema protegido

---

# 📱 6. MÓDULO DE INTERFACE E USABILIDADE

## 6.1 Responsividade

### TC062 - Layout Mobile - Login/Registro
**Prioridade:** Alta  
**Tags:** ui, responsive, mobile, authentication  

**Pré-condições:**
- Dispositivo móvel ou inspetor de browser

**Passos:**
1. Acessar páginas de login e registro em mobile
2. Verificar layout e funcionalidade
3. Testar formulários

**Resultado Esperado:**
- Layout adaptado para mobile
- Formulários utilizáveis
- Botões acessíveis
- Texto legível

**Critérios de Aceitação:**
- [ ] Layout responsivo
- [ ] Funcionalidade preservada
- [ ] UX adequada

---

### TC063 - Layout Mobile - Dashboard
**Prioridade:** Alta  
**Tags:** ui, responsive, mobile, dashboard  

**Pré-condições:**
- Usuário logado em dispositivo mobile

**Passos:**
1. Acessar dashboard em mobile
2. Testar funcionalidades principais
3. Verificar navegação

**Resultado Esperado:**
- Dashboard utilizável em mobile
- Menu de navegação adaptado
- Funcionalidades acessíveis
- Performance adequada

**Critérios de Aceitação:**
- [ ] Interface mobile-friendly
- [ ] Funcionalidades completas
- [ ] Navegação intuitiva

---

### TC064 - Layout Tablet - Páginas Principais
**Prioridade:** Média  
**Tags:** ui, responsive, tablet  

**Pré-condições:**
- Viewport de tablet

**Passos:**
1. Testar páginas principais em tablet
2. Verificar adaptação

**Resultado Esperado:**
- Layout adequado para tablets
- Aproveitamento do espaço disponível
- Interface híbrida mobile/desktop

**Critérios de Aceitação:**
- [ ] Layout tablet otimizado
- [ ] Espaço bem utilizado
- [ ] Interface adequada

---

## 6.2 Navegação e UX

### TC065 - Navegação - Estados de Autenticação
**Prioridade:** Alta  
**Tags:** ui, navigation, authentication  

**Pré-condições:**
- Aplicação em diferentes estados de auth

**Passos:**
1. Verificar menu para usuário não logado
2. Verificar menu para usuário logado
3. Testar transições entre estados

**Resultado Esperado:**
- Menu apropriado para cada estado
- Links relevantes disponíveis
- Transições suaves
- Estado sempre claro

**Critérios de Aceitação:**
- [ ] Menu contextual
- [ ] Estado claro
- [ ] Transições funcionais

---

### TC066 - Feedback Visual - Loading States
**Prioridade:** Média  
**Tags:** ui, feedback, loading  

**Pré-condições:**
- Operações que levam tempo

**Passos:**
1. Iniciar operações longas (upload, AI)
2. Verificar feedback visual
3. Testar cancelamento se aplicável

**Resultado Esperado:**
- Indicadores de loading visíveis
- Usuário informado sobre progresso
- Interface não bloqueia
- Cancelamento possível quando apropriado

**Critérios de Aceitação:**
- [ ] Loading indicators
- [ ] Feedback adequado
- [ ] Interface responsiva

---

### TC067 - Flash Messages
**Prioridade:** Média  
**Tags:** ui, feedback, messages  

**Pré-condições:**
- Ações que geram mensagens

**Passos:**
1. Executar ações diversas
2. Verificar mensagens exibidas
3. Testar diferentes tipos (sucesso, erro, aviso)

**Resultado Esperado:**
- Mensagens contextuais exibidas
- Diferentes tipos visualmente distintos
- Mensagens desaparecem automaticamente
- Conteúdo claro e útil

**Critérios de Aceitação:**
- [ ] Mensagens apropriadas
- [ ] Tipos visuais distintos
- [ ] Comportamento consistente

---

# 🔄 7. MÓDULO DE INTEGRAÇÃO E FLUXOS COMPLETOS

## 7.1 Fluxo Completo de Novo Usuário

### TC068 - Jornada Completa - Cadastro até Primeira Compra
**Prioridade:** Alta  
**Tags:** integration, user-journey, e2e  

**Pré-condições:**
- Sistema completamente funcional

**Passos:**
1. Acessar página inicial
2. Clicar em "Sign Up"
3. Completar cadastro
4. Verificar email
5. Fazer login
6. Explorar trial por alguns dias
7. Quando trial próximo do fim, fazer upgrade
8. Completar checkout
9. Usar funcionalidades completas

**Resultado Esperado:**
- Jornada completa sem fricções
- Cada etapa funcionando perfeitamente
- Dados consistentes em todas as fases
- Transição suave de trial para pago

**Critérios de Aceitação:**
- [ ] Fluxo completo funcional
- [ ] Dados consistentes
- [ ] UX fluida

---

### TC069 - Fluxo Completo - Google OAuth até Subscription
**Prioridade:** Alta  
**Tags:** integration, google-oauth, subscription, e2e  

**Pré-condições:**
- Google OAuth configurado

**Passos:**
1. Fazer login via Google (novo usuário)
2. Verificar trial automático
3. Usar funcionalidades durante trial
4. Fazer upgrade para plano pago
5. Confirmar subscription ativa

**Resultado Esperado:**
- Login Google funcional
- Trial iniciado automaticamente
- Upgrade sem problemas
- Integração completa

**Critérios de Aceitação:**
- [ ] OAuth funcional
- [ ] Trial automático
- [ ] Upgrade suave

---

### TC070 - Fluxo de Recuperação - Trial Expirado
**Prioridade:** Média  
**Tags:** integration, trial-recovery, subscription  

**Pré-condições:**
- Usuário com trial expirado

**Passos:**
1. Tentar acessar sistema com trial expirado
2. Ser redirecionado para pricing
3. Escolher plano e fazer upgrade
4. Recuperar acesso completo

**Resultado Esperado:**
- Bloqueio efetivo após expiração
- Caminho claro para reativação
- Upgrade restabelece acesso
- Dados preservados

**Critérios de Aceitação:**
- [ ] Bloqueio efetivo
- [ ] Caminho de recuperação claro
- [ ] Dados preservados

---

## 7.2 Fluxos de Billing Avançados

### TC071 - Ciclo Completo - Pagamento até Renovação
**Prioridade:** Média  
**Tags:** integration, billing, renewal  

**Pré-condições:**
- Subscription ativa próxima da renovação

**Passos:**
1. Aguardar data de renovação
2. Verificar cobrança automática
3. Confirmar renovação da subscription
4. Verificar continuidade do serviço

**Resultado Esperado:**
- Renovação automática funcionando
- Cobrança processada corretamente
- Serviço sem interrupção
- Webhooks processados

**Critérios de Aceitação:**
- [ ] Renovação automática
- [ ] Cobrança correta
- [ ] Continuidade do serviço

---

### TC072 - Fluxo de Cancelamento e Período Final
**Prioridade:** Média  
**Tags:** integration, cancellation, end-period  

**Pré-condições:**
- Subscription ativa

**Passos:**
1. Cancelar subscription
2. Usar serviço durante período final
3. Verificar bloqueio ao fim do período
4. Confirmar dados preservados

**Resultado Esperado:**
- Cancelamento no fim do período
- Acesso mantido durante período pago
- Bloqueio automático após fim
- Dados do usuário preservados

**Critérios de Aceitação:**
- [ ] Cancelamento correto
- [ ] Período de graça respeitado
- [ ] Bloqueio automático
- [ ] Dados preservados

---

# 🧪 8. TESTES DE LIMITE E PERFORMANCE

## 8.1 Limites de Uso

### TC073 - Limites de Trial - Textos e Documentos
**Prioridade:** Média  
**Tags:** limits, trial, usage  

**Pré-condições:**
- Usuário em trial
- Limites configurados no sistema

**Passos:**
1. Criar textos até atingir limite
2. Tentar criar texto adicional
3. Fazer upload de documentos até limite
4. Tentar upload adicional

**Resultado Esperado:**
- Limites respeitados conforme configurado
- Mensagens de erro quando limite atingido
- Upgrade oferecido como solução
- Sistema estável mesmo no limite

**Critérios de Aceitação:**
- [ ] Limites funcionando
- [ ] Mensagens apropriadas
- [ ] Sistema estável

---

### TC074 - Performance - Upload de Arquivo Grande
**Prioridade:** Baixa  
**Tags:** performance, upload, limits  

**Pré-condições:**
- Arquivo grande (próximo ao limite)

**Passos:**
1. Fazer upload de arquivo grande
2. Monitorar performance
3. Verificar feedback de progresso

**Resultado Esperado:**
- Upload processado adequadamente
- Feedback de progresso funcional
- Sistema responsivo
- Timeout adequado

**Critérios de Aceitação:**
- [ ] Performance aceitável
- [ ] Feedback funcional
- [ ] Sistema estável

---

### TC075 - Rate Limiting - APIs
**Prioridade:** Baixa  
**Tags:** security, rate-limiting, api  

**Pré-condições:**
- Rate limiting configurado

**Passos:**
1. Fazer múltiplas requisições rapidamente
2. Verificar bloqueio por rate limit
3. Aguardar reset do limit

**Resultado Esperado:**
- Rate limiting ativo
- Requisições bloqueadas após limite
- Reset automático após período
- Mensagem de erro apropriada

**Critérios de Aceitação:**
- [ ] Rate limiting funcional
- [ ] Bloqueio efetivo
- [ ] Reset automático

---

# ✅ 9. CRITÉRIOS DE ACEITAÇÃO GERAIS

## 9.1 Funcionalidades Básicas

**Todos os testes devem passar os seguintes critérios:**

- [ ] **Funcionalidade Core:** O recurso principal funciona conforme especificado
- [ ] **Tratamento de Erro:** Erros são tratados graciosamente
- [ ] **Validação:** Inputs são validados adequadamente
- [ ] **Segurança:** Dados sensíveis protegidos
- [ ] **Performance:** Tempo de resposta aceitável (<3s para operações normais)
- [ ] **UI/UX:** Interface intuitiva e responsiva
- [ ] **Dados:** Integridade de dados mantida

## 9.2 Testes Cross-Browser

**Navegadores Suportados:**
- [ ] Chrome (versão atual e anterior)
- [ ] Firefox (versão atual)
- [ ] Safari (versão atual)
- [ ] Edge (versão atual)

## 9.3 Testes de Dispositivos

**Dispositivos Testados:**
- [ ] Desktop (1920x1080, 1366x768)
- [ ] Tablet (iPad, Android tablet)
- [ ] Mobile (iPhone, Android phone)

---

# 📝 10. NOTAS DE EXECUÇÃO

## 10.1 Preparação do Ambiente

**Antes de iniciar os testes:**

1. **Verificar Configurações:**
   - [ ] DATABASE_URL configurada
   - [ ] STRIPE keys de teste configuradas
   - [ ] ANTHROPIC_API_KEY válida
   - [ ] GOOGLE_CLIENT_ID configurado
   - [ ] MAIL settings para Mailtrap

2. **Resetar Dados de Teste:**
   ```sql
   DELETE FROM payment_events WHERE created_at < NOW() - INTERVAL '1 day';
   DELETE FROM password_reset_tokens WHERE expires_at < NOW();
   DELETE FROM email_verification_tokens WHERE expires_at < NOW();
   ```

3. **Verificar Serviços Externos:**
   - [ ] Stripe Dashboard acessível
   - [ ] Mailtrap recebendo emails
   - [ ] Anthropic API respondendo
   - [ ] Google OAuth configurado

## 10.2 Durante a Execução

**Pontos de Atenção:**
- Sempre verificar logs da aplicação para erros
- Monitorar webhook do Stripe para eventos
- Confirmar emails no Mailtrap
- Verificar dados no banco após operações críticas
- Testar em modo incógnito para evitar cache

## 10.3 Documentação de Bugs

**Para cada bug encontrado:**
- [ ] Screenshot/screencast do problema
- [ ] Passos para reproduzir
- [ ] Comportamento esperado vs atual
- [ ] Logs relevantes
- [ ] Dados de ambiente
- [ ] Prioridade (Crítico/Alto/Médio/Baixo)

## 10.4 Relatório Final

**Métricas de Qualidade:**
- % de test cases passando
- Número de bugs por módulo
- Cobertura de funcionalidades
- Tempo total de execução
- Recomendações para melhoria

---

**Status:** 📋 Pronto para Execução  
**Última Atualização:** [Data]  
**Próxima Revisão:** [Data + 1 mês]

---

*Este documento deve ser mantido atualizado conforme a aplicação evolui. Novos test cases devem ser adicionados para novas funcionalidades.*