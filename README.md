# RPA Scraping System

Sistema de coleta de dados de múltiplas fontes web com gerenciamento de jobs através de filas de mensagens e API REST.

> 📋 Para detalhes completos dos requisitos técnicos, veja [REQUIREMENTS.md](REQUIREMENTS.md)

## ⚠️ Template Base - PREENCHER Configurações

Este repositório contém uma **estrutura base completa** para um sistema RPA de scraping com:
- ✅ **Type Hints** em todo o código
- ✅ **Documentação completa** com docstrings
- ✅ **Testes unitários** prontos para execução
- ✅ **GitHub Actions** configurado para CI/CD
- ✅ **Arquitetura completa**: FastAPI + RabbitMQ + PostgreSQL + Selenium + BeautifulSoup

### 📝 O que você precisa PREENCHER:

1. **Configuração no `.env`** (copie de `.env.example`):
   - Credenciais do PostgreSQL (`DATABASE_URL`)
   - Credenciais do RabbitMQ (`RABBITMQ_HOST`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`)
   - URLs dos sites para scraping (`HOCKEY_URL`, `OSCAR_URL`)

2. **Seletores HTML/CSS nos scrapers**:
   - `app/static_scraper/hockey.py`: Adaptar seletores CSS conforme HTML do site
   - `app/dynamic_scraper/oscar.py`: Adaptar seletores Selenium conforme DOM do site

3. **GitHub Actions** (opcional):
   - Configurar secrets para deploy no GCR (`.github/workflows/ci.yml`)

Todos os pontos marcados com `# PREENCHER:` ou `"PREENCHER_*"` devem ser configurados conforme seu ambiente e site alvo.

## Estrutura do Projeto

```
├── app/
│   ├── core/             # Config, DB e Rabbit (O essencial)
│   │   ├── __init__.py
│   │   ├── config.py     # Configurações da aplicação
│   │   ├── database.py   # Conexão e sessão do banco
│   │   └── rabbitmq.py   # Conexão e gerenciamento de filas
│   ├── static_scraper/   # Hockey (BeautifulSoup)
│   │   ├── __init__.py
│   │   └── hockey.py     # Scraper para dados de Hockey
│   ├── dynamic_scraper/  # Oscar (Selenium)
│   │   ├── __init__.py
│   │   └── oscar.py      # Scraper para dados de Oscar
│   ├── __init__.py
│   ├── models.py         # DB (Job, HockeyData, OscarData)
│   ├── schemas.py        # Pydantic (Request/Response)
│   ├── worker.py         # O Consumer do RabbitMQ que chama os scrapers
│   └── main.py           # FastAPI (Endpoints e disparo de mensagens)
├── tests/                # Testes de integração
│   ├── __init__.py
│   ├── conftest.py       # Fixtures e configuração de testes
│   └── test_api.py       # Testes de integração da API
├── .env.example          # Exemplo de variáveis de ambiente
├── docker-compose.yml    # Orquestração de containers
├── Dockerfile            # Imagem Docker da aplicação
└── requirements.txt      # Dependências Python
```

## Arquitetura

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

## Como Executar

### Pré-requisitos

- Docker
- Docker Compose

### Passos

```bash
# 1. Copiar exemplo de variáveis de ambiente
cp .env.example .env

# 2. Subir os serviços
docker-compose up --build

# 3. Acessar os serviços
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# RabbitMQ Management: http://localhost:15672
```

## Endpoints da API

```
# Agendar coletas
POST /crawl/hockey         → Agenda coleta do Hockey (retorna job_id)
POST /crawl/oscar          → Agenda coleta do Oscar (retorna job_id)
POST /crawl/all            → Agenda ambas as coletas (retorna job_id)

# Gerenciar jobs
GET  /jobs                 → Lista todos os jobs
GET  /jobs/{job_id}        → Status e detalhes de um job

# Consultar resultados
GET  /jobs/{job_id}/results → Resultados de um job específico
GET  /results/hockey        → Todos os dados coletados de Hockey
GET  /results/oscar         → Todos os dados coletados de Oscar
```

## Desenvolvimento

### Ambiente Nix + direnv (Recomendado - Linux)

```bash
# Permitir direnv
direnv allow

# O ambiente será carregado automaticamente
```

### Testes

```bash
# Rodar todos os testes
pytest

# Rodar com coverage
pytest --cov=app tests/
```

### Linting

```bash
# Verificar código
ruff check app/ tests/

# Formatar código
black app/ tests/
```

## Stack Tecnológica

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM para PostgreSQL
- **RabbitMQ** - Sistema de filas de mensagens
- **BeautifulSoup4** - Scraping de páginas estáticas
- **Selenium** - Scraping de páginas dinâmicas
- **Docker** - Containerização
