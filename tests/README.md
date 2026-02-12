# Test Architecture Documentation

This document describes the test architecture for the RPA Scraping System.

## Structure

```
tests/
├── conftest.py          # Global fixtures (DB, Rabbit, App)
├── unit/
│   ├── test_parsers.py  # Validates scraping/HTML parsing logic
│   └── test_schemas.py  # Validates Pydantic data validation
└── integration/
    ├── test_api.py      # Tests API endpoints and Rabbit messaging
    └── test_worker.py   # Tests queue consumption and DB persistence
```

## Test Categories

### Unit Tests (`tests/unit/`)

**test_parsers.py** - Tests for HTML parsing and data extraction logic:
- `TestHockeyParser`: Validates BeautifulSoup parsing of hockey team data
- `TestOscarParser`: Validates parsing of Oscar award data structures

**test_schemas.py** - Tests for Pydantic schema validation:
- `TestJobSchemas`: Job creation and response schemas
- `TestHockeyDataSchemas`: Hockey data validation rules
- `TestOscarDataSchemas`: Oscar data validation rules
- `TestCrawlSchemas`: Crawl request/response schemas
- `TestSchemaInheritance`: ORM mode and schema inheritance

### Integration Tests (`tests/integration/`)

**test_api.py** - Tests for FastAPI endpoints and RabbitMQ integration:
- `TestCrawlEndpoints`: Job creation endpoints (POST /crawl/*)
- `TestJobManagementEndpoints`: Job status and retrieval (GET /jobs/*)
- `TestResultsEndpoints`: Results retrieval (GET /results/*)
- `TestAPIErrorHandling`: Error scenarios
- `TestRabbitMQIntegration`: Message publishing and routing

**test_worker.py** - Tests for RabbitMQ worker and database persistence:
- `TestWorkerQueueConsumption`: Message consumption from queues
- `TestWorkerDatabasePersistence`: Data persistence to PostgreSQL
- `TestWorkerScraperIntegration`: Worker calling scrapers correctly
- `TestWorkerTransactionHandling`: Database transaction management
- `TestWorkerConcurrency`: Handling multiple jobs

## Global Fixtures (`conftest.py`)

Available fixtures for all tests:

- **test_db**: In-memory SQLite database for isolated testing
- **test_client**: FastAPI TestClient with mocked dependencies
- **mock_rabbitmq**: Mocked RabbitMQ connection for unit testing
- **sample_hockey_html**: Sample HTML for testing hockey parser
- **sample_oscar_data**: Sample data for testing oscar parser

## Running Tests

```bash
# Run all tests
pytest tests/

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_parsers.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v tests/
```

## Test Statistics

- **Total Tests**: 59
  - Unit Tests: 25
    - test_parsers.py: 10 tests
    - test_schemas.py: 15 tests
  - Integration Tests: 34
    - test_api.py: 18 tests
    - test_worker.py: 16 tests

## Implementation Notes

The tests are currently implemented as **scaffolds** with placeholder `pass` statements. 
They are designed to be uncommented and activated as the corresponding application 
code is implemented:

1. Implement the feature (models, schemas, scrapers, API, worker)
2. Uncomment the relevant test code
3. Run the tests
4. Fix any issues
5. Verify all tests pass

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Fixtures**: Use fixtures from conftest.py to set up test dependencies
3. **Mocking**: Mock external services (RabbitMQ, web requests) in unit tests
4. **Database**: Use in-memory SQLite for fast, isolated database tests
5. **Assertions**: Use clear, descriptive assertions with helpful error messages
6. **Documentation**: Each test has a docstring explaining what it validates

## Example: Activating Tests

When you implement the hockey scraper, uncomment the tests in `test_parsers.py`:

```python
def test_parse_team_data_extraction(self, sample_hockey_html):
    """Test extracting actual values from team row."""
    from app.static_scraper.hockey import parse_team_row  # Import your implementation
    
    soup = BeautifulSoup(sample_hockey_html, "html.parser")
    row = soup.find("tr", class_="team")
    
    # Use your actual parser function
    data = parse_team_row(row)
    
    # Validate extracted values
    assert data["team_name"] == "Boston Bruins"
    assert data["year"] == 1990
    assert data["wins"] == 44
```

## Dependencies

Key testing dependencies (from requirements.txt):
- pytest==7.4.4
- pytest-asyncio==0.23.3
- httpx==0.26.0 (for FastAPI testing)
- beautifulsoup4==4.12.3 (for parser tests)
