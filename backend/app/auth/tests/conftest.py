import secrets
import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import select
import pytest

from app.auth.schemas import PrivateUser
from app.auth.models import Users, AuthSessions
from app.core.database import TestSessionLocal, get_db
from app.main import app
from app.auth.service import get_password_hash

@pytest.fixture
def session():
    with TestSessionLocal() as session:
        yield session
        session.query(Users).delete()
        session.query(AuthSessions).delete()
        session.commit()

@pytest.fixture
def client_override(session):
    def get_db_override():
        yield session
    
    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def add_user_in_db(session):

    session.add(
        Users(
            username= 'testtest',
            email= 'test@example.com',
            password_hash= get_password_hash('testtest')
        ))
    session.commit

    user = session.scalar(
        select(Users).where(
            Users.email == 'test@example.com'
            )
        )
    return user


@pytest.fixture
def add_auth_session_in_db(add_user_in_db, session):

    key = secrets.token_urlsafe(64)
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    session.add(
        AuthSessions(
            user_id= add_user_in_db.id,
            refresh_token_hash= key_hash,
        )
    )
    session.commit