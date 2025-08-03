import pytest
import asyncio
import os
import tempfile
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine for each test."""
    # Create a temporary file for each test
    db_fd, db_path = tempfile.mkstemp()
    test_db_url = f"sqlite:///{db_path}"
    
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if 'sqlite' in str(engine.url):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    yield engine
    
    # Cleanup
    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
async def async_client(test_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with test database."""
    def override_get_db():
        return test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")

def pytest_collection_modifyitems(config, items):
    """Modify collected test items."""
    for item in items:
        # Add asyncio marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
