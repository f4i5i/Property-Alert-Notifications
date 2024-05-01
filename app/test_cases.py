import pytest
import logging

from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .main import app, get_db
from .crud import get_user_preferences, create_or_update_user_preferences

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Test Database
@pytest.fixture(scope="module")
def engine():
    return create_engine('sqlite:///test.db', echo=True)

@pytest.fixture(scope="module")
def Base():
    return declarative_base()

@pytest.fixture(scope="module")
def SessionLocal(engine, Base):
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db(SessionLocal):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI client for testing routes
@pytest.fixture
async def client(test_db):
    async def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Tests
def test_create_user_preferences(test_db):
    test_preferences = {
        'user_id': '1', 
        'email_enabled': True, 
        'sms_enabled': False,
        'email': 'user@example.com',
        'phone_number': '1234567890'
    }
    response = create_or_update_user_preferences(test_db, **test_preferences)
    test_db.commit()
    assert response.user_id == 1
    assert response.email_enabled is True
    assert response.sms_enabled is False
    logger.info("test_create_user_preferences passed.")

def test_get_user_preferences(test_db):
    user_id = 1
    response = get_user_preferences(test_db, user_id)
    assert response.user_id == user_id
    logger.info("test_get_user_preferences passed.")

@pytest.mark.asyncio
async def test_update_preferences_route():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/preferences/1", json={
            "email_enabled": True,
            "sms_enabled": False,
            "email": "test@example.com",
            "phone_number": "1234567890"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == 1
    assert data['email_enabled'] is True
    assert data['sms_enabled'] is False
    logger.info("test_update_preferences_route passed.")

@pytest.mark.asyncio
async def test_same_preferences_route():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/preferences/21", json={
            "email_enabled": False,
            "sms_enabled": False,
            "email": "user21@gmail.com",
            "phone_number": "130321167"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == 21
    assert data['email_enabled'] is False
    assert data['sms_enabled'] is False
    logger.info("test_same_preferences_route passed.")

@pytest.mark.asyncio
async def test_different_preferences_route():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/preferences/42", json={
            "email_enabled": True,
            "sms_enabled": True,
            "email": "user42@example.com",
            "phone_number": "9876543210"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == 42
    assert data['email_enabled'] is True
    assert data['sms_enabled'] is True
    logger.info("test_different_preferences_route passed.")

@pytest.mark.asyncio
async def test_invalid_user_id_route():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/preferences/invalid", json={
            "email_enabled": True,
            "sms_enabled": True,
            "email": "invalid@example.com",
            "phone_number": "1234567890"
        })
    
    assert response.status_code == 422  # Assuming validation error returns status code 422
    logger.info("test_invalid_user_id_route passed.")
