"""
Global test configuration and fixtures.
Provides DB, RabbitMQ, and App fixtures for all tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after models are implemented
# from app.models import Base
# from app.main import app
# from app.core.database import get_db


@pytest.fixture(scope="function")
def test_db():
    """
    Creates an in-memory SQLite database for testing.
    Each test gets a fresh database that is cleaned up after the test.
    """
    # Use in-memory SQLite for fast, isolated tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    # Uncomment when models are implemented:
    # Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """
    Provides a FastAPI TestClient with overridden database dependency.
    """
    # Uncomment when app is implemented:
    # def override_get_db():
    #     try:
    #         yield test_db
    #     finally:
    #         pass
    #
    # app.dependency_overrides[get_db] = override_get_db
    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()

    # Temporary placeholder
    from app.main import app

    yield TestClient(app)


@pytest.fixture(scope="function")
def mock_rabbitmq(monkeypatch):
    """
    Mocks RabbitMQ connection for testing without actual RabbitMQ server.
    Useful for unit tests and some integration tests.
    """
    messages = []

    class MockChannel:
        def basic_publish(self, exchange, routing_key, body, properties=None):
            messages.append(
                {
                    "exchange": exchange,
                    "routing_key": routing_key,
                    "body": body,
                    "properties": properties,
                }
            )

        def queue_declare(self, queue, durable=False):
            pass

        def basic_consume(self, queue, on_message_callback, auto_ack=False):
            pass

    class MockConnection:
        def channel(self):
            return MockChannel()

        def close(self):
            pass

    def mock_connect(*args, **kwargs):
        return MockConnection()

    # This will be used to patch pika.BlockingConnection
    # monkeypatch.setattr("pika.BlockingConnection", mock_connect)

    yield messages


@pytest.fixture(scope="session")
def sample_hockey_html():
    """
    Sample HTML for testing Hockey scraper parser.
    """
    return """
    <table class="table">
        <tr class="team">
            <td class="name">Boston Bruins</td>
            <td class="year">1990</td>
            <td class="wins">44</td>
            <td class="losses">24</td>
            <td class="ot-losses">0</td>
            <td class="pct">0.550</td>
            <td class="gf">299</td>
            <td class="ga">264</td>
            <td class="diff">35</td>
        </tr>
    </table>
    """


@pytest.fixture(scope="session")
def sample_oscar_data():
    """
    Sample data structure for testing Oscar scraper parser.
    """
    return [
        {
            "year": 2010,
            "title": "The Hurt Locker",
            "nominations": 9,
            "awards": 6,
            "best_picture": True,
        },
        {
            "year": 2010,
            "title": "Avatar",
            "nominations": 9,
            "awards": 3,
            "best_picture": False,
        },
    ]
