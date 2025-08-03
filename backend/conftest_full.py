import pytest
import asyncio
import os
import tempfile
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest_asyncio

# Import app components
from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User, Role, user_roles
from app.models.item import Item
from app.models.item_category import ItemCategory
from app.core.security import get_password_hash

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
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
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
def override_get_db(test_db_session):
    """Override the get_db dependency with test database session."""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(override_get_db) -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

@pytest.fixture(scope="function")
def test_user(test_db_session) -> User:
    """Create a test user."""
    # Create admin role if it doesn't exist
    admin_role = test_db_session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        test_db_session.add(admin_role)
        test_db_session.commit()
    
    # Create test user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    user.roles.append(admin_role)
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_manager_user(test_db_session) -> User:
    """Create a test manager user."""
    # Create manager role if it doesn't exist
    manager_role = test_db_session.query(Role).filter(Role.name == "manager").first()
    if not manager_role:
        manager_role = Role(name="manager", description="Manager role")
        test_db_session.add(manager_role)
        test_db_session.commit()
    
    # Create test user
    user = User(
        email="manager@example.com",
        full_name="Test Manager",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    user.roles.append(manager_role)
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_regular_user(test_db_session) -> User:
    """Create a test regular user without special roles."""
    user = User(
        email="regular@example.com",
        full_name="Regular User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_item_category(test_db_session) -> ItemCategory:
    """Create a test item category."""
    category = ItemCategory(
        name="Test Category",
        description="Test category description"
    )
    test_db_session.add(category)
    test_db_session.commit()
    test_db_session.refresh(category)
    return category

@pytest.fixture(scope="function")
def test_item(test_db_session, test_item_category) -> Item:
    """Create a test item."""
    item = Item(
        item_code="TEST001",
        name="Test Item",
        description="Test item description",
        category_id=test_item_category.id
    )
    test_db_session.add(item)
    test_db_session.commit()
    test_db_session.refresh(item)
    return item

@pytest.fixture(scope="function")
def auth_headers(test_user) -> dict:
    """Create authentication headers for test user."""
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def manager_auth_headers(test_manager_user) -> dict:
    """Create authentication headers for manager user."""
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": test_manager_user.email})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def regular_auth_headers(test_regular_user) -> dict:
    """Create authentication headers for regular user."""
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": test_regular_user.email})
    return {"Authorization": f"Bearer {access_token}"}

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
