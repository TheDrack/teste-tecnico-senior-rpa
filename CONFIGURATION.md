# 📋 Guia de Configuração - RPA Scraping System

Este documento centraliza **TODAS** as informações de configuração necessárias para executar o sistema RPA.

> 💡 **Mantenha este arquivo como referência principal para configuração**

---

## 🎯 Informações Extraídas de REQUIREMENTS.md

As seguintes informações foram preenchidas automaticamente com base no documento de requisitos:

### URLs dos Sites para Scraping

| Campo | Valor | Status |
|-------|-------|--------|
| **HOCKEY_URL** | `https://www.scrapethissite.com/pages/forms/` | ✅ Preenchido |
| **OSCAR_URL** | `https://www.scrapethissite.com/pages/ajax-javascript/` | ✅ Preenchido |

### Dados a Coletar

#### Hockey Teams
- Team Name
- Year
- Wins, Losses, OT Losses
- Win %, Goals For (GF), Goals Against (GA), Goal Difference

#### Oscar Winning Films
- Year
- Title
- Nominations
- Awards
- Best Picture

---

## 🔐 Configurações Sensíveis - PREENCHER

As seguintes configurações contêm dados sensíveis e devem ser configuradas manualmente:

### PostgreSQL Database

| Campo | Valor para Desenvolvimento Local | Valor para Produção | Status |
|-------|----------------------------------|---------------------|--------|
| **DATABASE_URL** | `postgresql://rpa_user:rpa_password@postgres:5432/rpa_db` | Use GitHub Secrets | 🔄 PREENCHER |
| **Host** | `postgres` (Docker) ou `localhost` | Seu servidor PostgreSQL | 🔄 PREENCHER |
| **Porta** | `5432` | `5432` (padrão) | ✅ Preenchido |
| **Usuário** | `rpa_user` (Docker Compose) | Seu usuário | 🔄 PREENCHER |
| **Senha** | `rpa_password` (Docker Compose) | Sua senha | 🔄 PREENCHER |
| **Database** | `rpa_db` (Docker Compose) | Seu database | 🔄 PREENCHER |
| **Pool Size** | `5` | `5` (padrão) | ✅ Preenchido |
| **Max Overflow** | `10` | `10` (padrão) | ✅ Preenchido |

### RabbitMQ Message Queue

| Campo | Valor para Desenvolvimento Local | Valor para Produção | Status |
|-------|----------------------------------|---------------------|--------|
| **RABBITMQ_HOST** | `rabbitmq` (Docker) | Seu servidor RabbitMQ | 🔄 PREENCHER |
| **RABBITMQ_PORT** | `5672` | `5672` (padrão) | ✅ Preenchido |
| **RABBITMQ_USER** | `rpa_user` (Docker Compose) | Seu usuário | 🔄 PREENCHER |
| **RABBITMQ_PASSWORD** | `rpa_password` (Docker Compose) | Sua senha | 🔄 PREENCHER |
| **RABBITMQ_QUEUE_HOCKEY** | `scraper_hockey_queue` | `scraper_hockey_queue` | ✅ Preenchido |
| **RABBITMQ_QUEUE_OSCAR** | `scraper_oscar_queue` | `scraper_oscar_queue` | ✅ Preenchido |

### Portas de Acesso (Para Produção)

| Serviço | Porta | Descrição | Como Configurar |
|---------|-------|-----------|-----------------|
| **API FastAPI** | `8000` | Endpoint principal da API | Use GitHub Environment: `${{ secrets.API_PORT }}` |
| **PostgreSQL** | `5432` | Conexão com banco de dados | Use GitHub Environment: `${{ secrets.DB_PORT }}` |
| **RabbitMQ** | `5672` | Fila de mensagens | Use GitHub Environment: `${{ secrets.RABBITMQ_PORT }}` |
| **RabbitMQ Management** | `15672` | Interface de gerenciamento | Use GitHub Environment: `${{ secrets.RABBITMQ_MGMT_PORT }}` |

---

## ⚙️ Configurações da Aplicação

Estas configurações já estão preenchidas com valores padrão:

| Campo | Valor | Descrição |
|-------|-------|-----------|
| **APP_NAME** | `RPA Scraping System` | Nome da aplicação |
| **DEBUG** | `False` | Modo debug (use `True` em desenvolvimento) |
| **API_PREFIX** | `/api/v1` | Prefixo das rotas da API |

### Configurações dos Scrapers

| Campo | Valor | Descrição |
|-------|-------|-----------|
| **SELENIUM_HEADLESS** | `True` | Executar Selenium sem interface gráfica |
| **SELENIUM_TIMEOUT** | `30` | Timeout padrão (segundos) |
| **SCRAPER_USER_AGENT** | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36` | User agent para requests |
| **SCRAPER_DELAY** | `1.0` | Delay entre requests (segundos) |

---

## 🔧 Como Configurar

### Opção 1: Desenvolvimento Local com Docker Compose (Recomendado)

1. **Copie o arquivo de exemplo:**
   ```bash
   cp .env.example .env
   ```

2. **O .env já está configurado para Docker Compose:**
   - PostgreSQL: `postgresql://rpa_user:rpa_password@postgres:5432/rpa_db`
   - RabbitMQ: host=`rabbitmq`, user=`rpa_user`, password=`rpa_password`
   - URLs dos sites já preenchidas

3. **Execute:**
   ```bash
   docker-compose up --build
   ```

### Opção 2: Produção com GitHub Actions e Secrets

1. **Configure os seguintes Secrets no GitHub:**
   
   Acesse: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

   | Nome do Secret | Descrição | Exemplo |
   |----------------|-----------|---------|
   | `DATABASE_URL` | URL completa do PostgreSQL | `postgresql://user:pass@host:5432/db` |
   | `RABBITMQ_HOST` | Host do RabbitMQ | `rabbitmq.exemplo.com` |
   | `RABBITMQ_PORT` | Porta do RabbitMQ | `5672` |
   | `RABBITMQ_USER` | Usuário do RabbitMQ | `seu_usuario` |
   | `RABBITMQ_PASSWORD` | Senha do RabbitMQ | `sua_senha_secreta` |
   | `API_PORT` | Porta da API | `8000` |
   | `DB_PORT` | Porta do PostgreSQL | `5432` |
   | `RABBITMQ_MGMT_PORT` | Porta do Management UI | `15672` |

2. **No GitHub Actions workflow (`.github/workflows/ci.yml`):**
   
   Os secrets são acessados usando a sintaxe:
   ```yaml
   env:
     DATABASE_URL: ${{ secrets.DATABASE_URL }}
     RABBITMQ_HOST: ${{ secrets.RABBITMQ_HOST }}
     RABBITMQ_PORT: ${{ secrets.RABBITMQ_PORT }}
     RABBITMQ_USER: ${{ secrets.RABBITMQ_USER }}
     RABBITMQ_PASSWORD: ${{ secrets.RABBITMQ_PASSWORD }}
   ```

### Opção 3: Produção Manual

1. **Copie e edite o .env:**
   ```bash
   cp .env.example .env
   nano .env  # ou vim, code, etc.
   ```

2. **Preencha manualmente todos os campos marcados com `PREENCHER_*`**

3. **Configure seu servidor PostgreSQL e RabbitMQ**

4. **Execute a aplicação:**
   ```bash
   # Instalar dependências
   pip install -r requirements.txt
   
   # Inicializar banco
   python -c "from app.core.database import init_db; init_db()"
   
   # Executar API
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # Em outro terminal, executar worker
   python -m app.worker
   ```

---

## 📝 Checklist de Configuração

Use este checklist para garantir que tudo está configurado:

### Configuração Básica
- [ ] Copiou `.env.example` para `.env`
- [ ] URLs dos sites já preenchidas (Hockey e Oscar)
- [ ] Configurou credenciais do PostgreSQL
- [ ] Configurou credenciais do RabbitMQ
- [ ] Testou conexão com PostgreSQL
- [ ] Testou conexão com RabbitMQ

### Docker Compose (Desenvolvimento)
- [ ] Docker e Docker Compose instalados
- [ ] Executou `docker-compose up --build`
- [ ] Acessou API Docs em http://localhost:8000/docs
- [ ] Acessou RabbitMQ Management em http://localhost:15672

### GitHub Actions (CI/CD)
- [ ] Configurou todos os secrets necessários
- [ ] Testou workflow de lint
- [ ] Testou workflow de testes
- [ ] Testou workflow de build
- [ ] (Opcional) Configurou deploy para GCR

### Scrapers
- [ ] Verificou URLs dos sites (Hockey e Oscar)
- [ ] Adaptou seletores CSS em `app/static_scraper/hockey.py`
- [ ] Adaptou seletores Selenium em `app/dynamic_scraper/oscar.py`
- [ ] Testou scrapers localmente

---

## 🚨 Valores que NÃO devem ser commitados

**NUNCA** commite os seguintes valores no repositório:

- ❌ Senhas de banco de dados
- ❌ Credenciais do RabbitMQ
- ❌ Tokens de API
- ❌ Chaves privadas
- ❌ Credenciais GCP

**SEMPRE** use:
- ✅ Arquivo `.env` local (já está no `.gitignore`)
- ✅ GitHub Secrets para CI/CD
- ✅ Environment Variables no servidor de produção

---

## 🔍 Onde Encontrar Cada Configuração

### No Código

- **config.py**: `app/core/config.py`
- **.env.example**: `.env.example`
- **docker-compose.yml**: `docker-compose.yml`

### No GitHub

- **Secrets**: `Repository` → `Settings` → `Secrets and variables` → `Actions`
- **Workflows**: `.github/workflows/ci.yml`

### Documentação de Referência

- **REQUIREMENTS.md**: Requisitos técnicos originais
- **README.md**: Visão geral e quick start
- **TEMPLATE.md**: Guia detalhado de uso do template
- **CONFIGURATION.md**: Este arquivo (referência de configuração)

---

## 💡 Dicas

1. **Para desenvolvimento local**: Use Docker Compose, é o mais simples
2. **Para produção**: Use GitHub Secrets e nunca exponha credenciais
3. **Teste sempre localmente antes de fazer deploy**
4. **Use diferentes credenciais para desenvolvimento e produção**
5. **Mantenha backup das configurações de produção em local seguro**

---

## 📞 Suporte

Em caso de dúvidas sobre configuração:
1. Verifique este arquivo (CONFIGURATION.md)
2. Leia TEMPLATE.md para guia detalhado
3. Consulte REQUIREMENTS.md para especificações originais
4. Entre em contato: ti@bpcreditos.com.br | gabrielpelizzaro@gmail.com
