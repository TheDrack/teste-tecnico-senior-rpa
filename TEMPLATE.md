# Guia de Uso do Template RPA

Este documento explica como usar este template para criar seu próprio sistema de scraping RPA.

> ⚙️ **Para referência completa de configuração, veja [CONFIGURATION.md](CONFIGURATION.md)**

## 📋 Visão Geral

Este template fornece uma estrutura completa e pronta para uso de um sistema RPA com:
- API REST (FastAPI)
- Processamento assíncrono de jobs (RabbitMQ)
- Persistência de dados (PostgreSQL)
- Scrapers estáticos (BeautifulSoup) e dinâmicos (Selenium)
- Testes automatizados
- CI/CD com GitHub Actions

**TODO O CÓDIGO JÁ ESTÁ IMPLEMENTADO** com Type Hints, documentação completa e comentários explicativos.

## 🚀 Começando

### 1. Configurar Variáveis de Ambiente

> ⚙️ **Veja [CONFIGURATION.md](CONFIGURATION.md) para lista completa de todas as configurações**

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e preencher as variáveis marcadas com PREENCHER_*
```

**URLs dos sites já preenchidas de REQUIREMENTS.md:**
- Hockey: `https://www.scrapethissite.com/pages/forms/`
- Oscar: `https://www.scrapethissite.com/pages/ajax-javascript/`

Variáveis principais a configurar:

```env
# Banco de dados PostgreSQL
DATABASE_URL=postgresql://SEU_USER:SUA_SENHA@SEU_HOST:SUA_PORTA/SEU_DB

# RabbitMQ
RABBITMQ_HOST=SEU_HOST_RABBITMQ
RABBITMQ_PORT=SUA_PORTA_RABBITMQ
RABBITMQ_USER=SEU_USER
RABBITMQ_PASSWORD=SUA_SENHA

# URLs dos sites (já preenchidas de REQUIREMENTS.md)
HOCKEY_URL=https://www.scrapethissite.com/pages/forms/
OSCAR_URL=https://www.scrapethissite.com/pages/ajax-javascript/

# Para produção, use GitHub Secrets em vez de valores hardcoded
# Veja CONFIGURATION.md para detalhes
```

### 2. Adaptar os Scrapers

#### Hockey Scraper (BeautifulSoup - Sites Estáticos)

Arquivo: `app/static_scraper/hockey.py`

Locais marcados com `# ADAPTAR` ou `# PREENCHER`:

```python
# Exemplo: Adaptar seletores CSS
rows = soup.find_all("tr", class_="team")  # ADAPTAR classe conforme HTML do site
team_name_elem = row.find("td", class_="name")  # ADAPTAR classe
```

**O que fazer:**
1. Inspecionar o HTML do site alvo
2. Identificar os seletores CSS corretos para os dados desejados
3. Substituir as classes exemplo pelas classes reais

#### Oscar Scraper (Selenium - Sites Dinâmicos)

Arquivo: `app/dynamic_scraper/oscar.py`

Locais marcados com `# ADAPTAR` ou `# PREENCHER`:

```python
# Exemplo: Aguardar elemento AJAX
self.wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "film"))  # ADAPTAR seletor
)

# Exemplo: Encontrar elementos
movie_elements = self.driver.find_elements(By.CLASS_NAME, "film")  # ADAPTAR
```

**O que fazer:**
1. Inspecionar o DOM do site alvo (F12 no navegador)
2. Identificar os seletores corretos (classe, ID, XPath)
3. Substituir os seletores exemplo pelos reais
4. Ajustar tempos de espera se necessário

### 3. Executar Localmente

#### Com Docker Compose (Recomendado)

```bash
# Subir todos os serviços
docker-compose up --build

# Acessar:
# - API: http://localhost:8000/docs
# - RabbitMQ: http://localhost:15672
```

#### Sem Docker (Para Desenvolvimento)

```bash
# Instalar dependências
pip install -r requirements.txt

# Inicializar banco (criar tabelas)
python -c "from app.core.database import init_db; init_db()"

# Executar API
uvicorn app.main:app --reload

# Em outro terminal, executar worker
python -m app.worker
```

### 4. Testar a API

```bash
# Agendar scraping de Hockey
curl -X POST http://localhost:8000/crawl/hockey

# Verificar status do job
curl http://localhost:8000/jobs/1

# Ver resultados
curl http://localhost:8000/jobs/1/results
```

## 📚 Estrutura de Código

### Core Modules (`app/core/`)

**`config.py`** - Configurações da aplicação
- Carrega variáveis do `.env`
- Validação com Pydantic
- Type Hints garantidos

**`database.py`** - Gerenciamento de banco de dados
- Engine SQLAlchemy
- Session factory
- Dependency injection para FastAPI

**`rabbitmq.py`** - Gerenciamento de filas
- Conexão com RabbitMQ
- Publicação de mensagens
- Consumo de mensagens

### Models (`app/models.py`)

Define tabelas do banco de dados:
- `Job`: Jobs de scraping
- `HockeyData`: Dados coletados de Hockey
- `OscarData`: Dados coletados de Oscar

Todos com Type Hints e relacionamentos.

### Schemas (`app/schemas.py`)

Schemas Pydantic para validação:
- Request/Response da API
- Validação de tipos
- Serialização automática

### Scrapers

**`app/static_scraper/hockey.py`**
- Scraping com BeautifulSoup
- Para sites HTML estáticos
- Suporte a paginação

**`app/dynamic_scraper/oscar.py`**
- Scraping com Selenium
- Para sites com JavaScript/AJAX
- Suporte a esperas e interações

### Worker (`app/worker.py`)

Consumer do RabbitMQ que:
1. Escuta filas de mensagens
2. Executa scrapers correspondentes
3. Salva dados no PostgreSQL
4. Atualiza status dos jobs

### API (`app/main.py`)

FastAPI com endpoints:
- `POST /crawl/{type}`: Agendar scraping
- `GET /jobs`: Listar jobs
- `GET /jobs/{id}`: Detalhes do job
- `GET /jobs/{id}/results`: Resultados do job
- `GET /results/{type}`: Todos os dados de um tipo

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Apenas unitários
pytest tests/unit/

# Com coverage
pytest --cov=app tests/
```

### Estrutura de Testes

- `tests/unit/test_parsers.py`: Testa parsing de HTML
- `tests/unit/test_schemas.py`: Testa validação Pydantic
- `tests/integration/`: Testes de integração (TODO: implementar)

## 🔄 CI/CD

GitHub Actions configurado em `.github/workflows/ci.yml`:

1. **Lint**: Verifica qualidade do código (Ruff, Black, MyPy)
2. **Test**: Executa testes unitários e de integração
3. **Build**: Constrói imagem Docker
4. **Deploy** (opcional): Push para GCR

### Configurar Deploy

Para habilitar deploy para Google Container Registry:

1. Criar service account no GCP
2. Adicionar secrets no GitHub:
   - `GCP_CREDENTIALS`: JSON da service account
   - `GCP_PROJECT_ID`: ID do projeto GCP
3. Descomentar seção de deploy no `ci.yml`

## 📝 Checklist de Customização

- [ ] Copiar `.env.example` para `.env`
- [ ] Preencher credenciais do PostgreSQL no `.env`
- [ ] Preencher credenciais do RabbitMQ no `.env`
- [ ] Configurar URLs dos sites alvo no `.env`
- [ ] Adaptar seletores CSS em `hockey.py`
- [ ] Adaptar seletores Selenium em `oscar.py`
- [ ] Testar scrapers localmente
- [ ] Ajustar tempos de espera se necessário
- [ ] Executar testes: `pytest`
- [ ] Executar lint: `ruff check app/`
- [ ] Formatar código: `black app/`
- [ ] Subir com Docker Compose
- [ ] Testar API endpoints
- [ ] Configurar secrets do GitHub para CI/CD (opcional)

## 🛠️ Dicas de Desenvolvimento

### Inspecionar Sites para Scraping

1. Abra o site no navegador
2. Pressione F12 (DevTools)
3. Use "Inspect Element" para ver HTML/DOM
4. Identifique classes, IDs e estrutura
5. Teste seletores no Console:
   ```javascript
   // Para BeautifulSoup (CSS)
   document.querySelector(".sua-classe")
   
   // Para Selenium (XPath)
   $x("//div[@class='sua-classe']")
   ```

### Debug de Scrapers

```python
# Hockey (BeautifulSoup)
from app.static_scraper.hockey import HockeyScraper

scraper = HockeyScraper()
data = scraper.scrape_page(1)
print(data)

# Oscar (Selenium)
from app.dynamic_scraper.oscar import OscarScraper

scraper = OscarScraper()
data = scraper.scrape_all_data()
print(data)
scraper.close()
```

### Adicionar Novos Tipos de Scraping

1. Criar novo scraper em `app/scrapers/`
2. Adicionar modelo em `app/models.py`
3. Adicionar schema em `app/schemas.py`
4. Criar endpoint em `app/main.py`
5. Adicionar lógica no `app/worker.py`
6. Criar testes

## 🐛 Solução de Problemas

### Erro ao conectar PostgreSQL
- Verificar se PostgreSQL está rodando
- Conferir credenciais no `.env`
- Testar conexão: `psql -h HOST -U USER -d DB`

### Erro ao conectar RabbitMQ
- Verificar se RabbitMQ está rodando
- Conferir credenciais no `.env`
- Acessar management UI: `http://localhost:15672`

### Selenium não encontra elementos
- Aumentar `SELENIUM_TIMEOUT` no `.env`
- Verificar se seletores estão corretos
- Testar com headless=False para ver navegador

### Testes falhando
- Instalar dependências: `pip install -r requirements.txt`
- Limpar cache: `pytest --cache-clear`
- Executar com verbose: `pytest -vv`

## 📚 Recursos Adicionais

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [RabbitMQ Tutorial](https://www.rabbitmq.com/getstarted.html)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Docs](https://selenium-python.readthedocs.io/)
- [Pydantic Docs](https://docs.pydantic.dev/)

## 💡 Suporte

Para dúvidas ou problemas:
1. Verifique os comentários no código (marcados com `PREENCHER` ou `ADAPTAR`)
2. Leia a documentação das bibliotecas usadas
3. Execute os testes para validar mudanças
4. Use o linter para verificar qualidade do código
