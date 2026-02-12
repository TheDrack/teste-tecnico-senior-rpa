# RPA Scraping System

Sistema de coleta de dados de múltiplas fontes web com gerenciamento de jobs através de filas de mensagens e API REST.

[![Tests](https://img.shields.io/badge/tests-59%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange)](https://www.sqlalchemy.org/)

> 📋 **Documentação Completa**:
> - [REQUIREMENTS.md](REQUIREMENTS.md) - Especificações técnicas originais
> - [CONFIGURATION.md](CONFIGURATION.md) - Guia de configuração completo
> - [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Detalhes da refatoração recente

## 🎯 Visão Geral

Sistema completo de scraping web com arquitetura moderna e assíncrona:

- ✅ **API REST** com FastAPI (10 endpoints)
- ✅ **Processamento assíncrono** com RabbitMQ
- ✅ **Persistência** em PostgreSQL com SQLAlchemy
- ✅ **Scrapers** estáticos (BeautifulSoup) e dinâmicos (Selenium)
- ✅ **Testes** completos (59 testes unitários e de integração)
- ✅ **CI/CD** com GitHub Actions
- ✅ **Type hints** em 100% do código
- ✅ **Docker** e docker-compose prontos para uso

### 📊 Status do Projeto

| Categoria | Status |
|-----------|--------|
| **Testes** | ✅ 59/59 passando |
| **Cobertura** | ✅ Completa |
| **Type Hints** | ✅ 100% |
| **Documentação** | ✅ Completa |
| **CI/CD** | ✅ Configurado |
| **Deprecations** | ✅ 1 warning (biblioteca externa) |

## 🚀 Quick Start

### Com Docker (Recomendado)

```bash
# 1. Clonar repositório
git clone <repo-url>
cd teste-tecnico-senior-rpa

# 2. Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais (ou usar valores padrão do docker-compose)

# 3. Iniciar todos os serviços
docker-compose up --build

# 4. Acessar aplicação
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# RabbitMQ: http://localhost:15672 (guest/guest)
```

### Sem Docker

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
export RABBITMQ_HOST="localhost"
# ... outras variáveis

# 3. Inicializar banco
python -c "from app.core.database import init_db; init_db()"

# 4. Iniciar API
uvicorn app.main:app --reload

# 5. Iniciar Worker (em outro terminal)
python -m app.worker
```

## 📚 Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  RabbitMQ   │────▶│   Workers   │
│    (API)    │     │   (Queue)   │     │  (Crawlers) │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │            ┌─────────────┐            │
       └───────────▶│  PostgreSQL │◀───────────┘
                    │    (Data)   │
                    └─────────────┘
```

### Fluxo de Trabalho

1. **Cliente** faz POST para `/crawl/hockey` ou `/crawl/oscar`
2. **API** cria job no banco e publica mensagem no RabbitMQ
3. **Worker** consome mensagem e executa scraper
4. **Scraper** coleta dados e salva no PostgreSQL
5. **Cliente** consulta status via `/jobs/{id}` e resultados via `/jobs/{id}/results`

## 📖 API Endpoints

### Scraping (Assíncrono)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/crawl/hockey` | Agenda coleta de dados de Hockey |
| `POST` | `/crawl/oscar` | Agenda coleta de dados de Oscar |
| `POST` | `/crawl/all` | Agenda ambas as coletas |

### Gerenciamento de Jobs

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/jobs` | Lista todos os jobs |
| `GET` | `/jobs/{job_id}` | Detalhes de um job específico |
| `GET` | `/jobs/{job_id}/results` | Resultados coletados por um job |

### Consulta de Dados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/results/hockey` | Todos os dados de Hockey coletados |
| `GET` | `/results/oscar` | Todos os dados de Oscar coletados |

### Exemplo de Uso

```bash
# 1. Agendar scraping
curl -X POST http://localhost:8000/crawl/hockey
# Response: {"job_id": 1, "message": "...", "status": "pending"}

# 2. Verificar status
curl http://localhost:8000/jobs/1
# Response: {"id": 1, "type": "hockey", "status": "running", ...}

# 3. Obter resultados
curl http://localhost:8000/jobs/1/results
# Response: {"job": {...}, "hockey_data": [...], "oscar_data": []}
```

## 🏗️ Estrutura do Projeto

```
teste-tecnico-senior-rpa/
├── app/
│   ├── core/              # ⚙️ Infraestrutura
│   │   ├── config.py      # Configurações (Pydantic Settings)
│   │   ├── database.py    # SQLAlchemy engine e sessões
│   │   └── rabbitmq.py    # Conexão RabbitMQ
│   ├── static_scraper/    # 🌐 Scrapers estáticos (BeautifulSoup)
│   │   └── hockey.py      # Scraper de Hockey
│   ├── dynamic_scraper/   # 🔄 Scrapers dinâmicos (Selenium)
│   │   └── oscar.py       # Scraper de Oscar
│   ├── models.py          # 🗄️ SQLAlchemy models
│   ├── schemas.py         # ✅ Pydantic schemas (validação)
│   ├── main.py            # 🚀 FastAPI app
│   └── worker.py          # 👷 RabbitMQ consumer
├── tests/
│   ├── unit/              # 🧪 Testes unitários (25)
│   │   ├── test_parsers.py
│   │   └── test_schemas.py
│   └── integration/       # 🔗 Testes de integração (34)
│       ├── test_api.py
│       └── test_worker.py
├── .github/workflows/     # 🔄 CI/CD
│   └── ci.yml             # GitHub Actions
├── docker-compose.yml     # 🐳 Orquestração
├── Dockerfile             # 📦 Imagem da aplicação
├── requirements.txt       # 📋 Dependências
└── .env.example          # 🔐 Template de configuração
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/

# Modo verbose
pytest -v
```

**Status**: ✅ 59/59 testes passando

## 🔧 Desenvolvimento

### Linting e Formatação

```bash
# Verificar código
ruff check app/ tests/

# Formatar código
black app/ tests/

# Type checking
mypy app/ --ignore-missing-imports
```

### Ambiente Nix (Linux)

```bash
# Permitir direnv
direnv allow

# Ambiente será carregado automaticamente
# Veja flake.nix para detalhes
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
# Database
DATABASE_URL=postgresql://rpa_user:rpa_password@postgres:5432/rpa_db

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=rpa_user
RABBITMQ_PASSWORD=rpa_password

# URLs dos sites (já configuradas)
HOCKEY_URL=https://www.scrapethissite.com/pages/forms/
OSCAR_URL=https://www.scrapethissite.com/pages/ajax-javascript/

# Scrapers
SELENIUM_HEADLESS=true
SCRAPER_DELAY=1.0
```

> 📖 **Veja [CONFIGURATION.md](CONFIGURATION.md)** para referência completa

### GitHub Secrets (Produção)

Configure em: `Settings` → `Secrets and variables` → `Actions`

```yaml
DATABASE_URL: <postgresql://...>
RABBITMQ_HOST: <host>
RABBITMQ_PORT: <5672>
RABBITMQ_USER: <user>
RABBITMQ_PASSWORD: <password>
```

## 📦 Stack Tecnológica

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.11+ | Linguagem base |
| **FastAPI** | 0.109+ | Framework web |
| **SQLAlchemy** | 2.0+ | ORM |
| **PostgreSQL** | 15+ | Banco de dados |
| **RabbitMQ** | 3.12+ | Message broker |
| **Pydantic** | 2.5+ | Validação de dados |
| **BeautifulSoup4** | 4.12+ | Scraping estático |
| **Selenium** | 4.16+ | Scraping dinâmico |
| **Docker** | 24+ | Containerização |
| **pytest** | 7.4+ | Framework de testes |

## 🎯 Features Implementadas

### ✅ Requisitos Funcionais

- [x] Coleta de dados de duas fontes distintas
- [x] Estratégias diferentes de scraping (estático + dinâmico)
- [x] Sistema de filas com RabbitMQ
- [x] Persistência em PostgreSQL
- [x] API REST assíncrona
- [x] Testes automatizados (unitários + integração)
- [x] Containerização com Docker
- [x] CI/CD com GitHub Actions

### ✅ Requisitos Técnicos

- [x] FastAPI para API
- [x] Pydantic para validação
- [x] SQLAlchemy como ORM
- [x] PostgreSQL como banco
- [x] RabbitMQ para filas
- [x] BeautifulSoup para páginas estáticas
- [x] Selenium para páginas dinâmicas
- [x] Docker + Docker Compose
- [x] GitHub Actions para CI/CD

### ✅ Qualidade de Código

- [x] Type hints em 100% do código
- [x] Docstrings completas
- [x] SOLID principles
- [x] DRY (Don't Repeat Yourself)
- [x] Separação de responsabilidades
- [x] Error handling robusto
- [x] Logging profissional
- [x] Zero código duplicado

## 🔄 Melhorias Recentes

Veja [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) para detalhes completos.

### Highlights

- ✅ Migração para SQLAlchemy 2.0 (DeclarativeBase)
- ✅ Atualização para FastAPI lifespan events
- ✅ Sistema de logging profissional
- ✅ Refatoração de código duplicado (-60 linhas)
- ✅ Inicialização automática do banco
- ✅ Error handling melhorado
- ✅ Redução de warnings de 4 para 1

## 📝 Roadmap

### Implementado ✅

- [x] Arquitetura básica
- [x] API REST completa
- [x] Sistema de workers
- [x] Scrapers funcio nais
- [x] Testes completos
- [x] CI/CD configurado
- [x] Refatoração e modernização

### Próximos Passos 🚧

- [ ] Alembic para migrations
- [ ] Cache layer (Redis)
- [ ] Rate limiting
- [ ] API authentication
- [ ] Monitoring (Sentry, Prometheus)
- [ ] Deploy em produção

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto foi desenvolvido como teste técnico.

## 📧 Contato

Para dúvidas ou sugestões:
- Email: ti@bpcreditos.com.br
- Email: gabrielpelizzaro@gmail.com

---

**Desenvolvido com ❤️ usando FastAPI, RabbitMQ e PostgreSQL**
