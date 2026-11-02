"""Test configuration and fixtures."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db, PromptTemplate


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    # Clear database before each test
    test_db_session.execute(delete(PromptTemplate))
    test_db_session.commit()
    
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    test_client = AsyncClient(transport=transport, base_url="http://test")
    yield test_client
    app.dependency_overrides.clear()
