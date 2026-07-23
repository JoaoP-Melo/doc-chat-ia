import hashlib
import secrets

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from app.auth.models import AuthSessions, Users
from app.auth.service import get_password_hash
from app.core.database import TestSessionLocal, get_db
from app.core.security import create_token
from app.document.models import Documents, DocumentsChunks
from app.main import app


@pytest.fixture
def session():
    with TestSessionLocal() as session:
        yield session
        session.query(Users).delete()
        session.query(AuthSessions).delete()
        session.query(Documents).delete()
        session.query(DocumentsChunks).delete()
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
            username="testtest",
            email="test@example.com",
            password_hash=get_password_hash("testtest"),
        )
    )
    session.commit()

    user = session.scalar(select(Users).where(Users.email == "test@example.com"))

    return user


@pytest.fixture
def add_auth_session_in_db(add_user_in_db, session):

    key = secrets.token_urlsafe(64)
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    session.add(
        AuthSessions(
            user_id=add_user_in_db.id,
            refresh_token_hash=key_hash,
        )
    )
    session.commit()

    auth_session = session.scalar(
        select(AuthSessions).where(AuthSessions.refresh_token_hash == key_hash)
    )

    return {"auth_session": auth_session, "key": key}


@pytest.fixture
def access_token(add_user_in_db):
    return create_token(
        data={
            "email": add_user_in_db.email,
            "id": add_user_in_db.id,
        }
    )


@pytest.fixture
def refresh_token(add_auth_session_in_db: dict):
    return create_token(data={"key": add_auth_session_in_db.get("key")})


@pytest.fixture
def add_document_in_db(add_user_in_db, session):

    session.add(
        Documents(
            user_id=add_user_in_db.id,
            name="test document",
            extension="test",
        )
    )
    session.commit()

    document = session.scalar(
        select(Documents).where(Documents.name == "test document")
    )

    return document
