import hashlib
import secrets

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from app.auth.models import AuthSessions, Users
from app.auth.service import get_password_hash
from app.conversation.models import Conversations, Messages
from app.core.database import TestSessionLocal, get_db
from app.core.security import create_token
from app.document.models import Documents, DocumentsChunks
from app.main import app

REFRESH_TOKEN_EXPIRE_MINUTES = 10080
ACCESS_TOKEN_EXPIRE_MINUTES = 15

@pytest.fixture
def session():
    with TestSessionLocal() as session:
        yield session
        session.query(Users).delete()
        session.query(AuthSessions).delete()
        session.query(Messages).delete()
        session.query(Documents).delete()
        session.query(DocumentsChunks).delete()
        session.query(Conversations).delete()
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
        data={ "email": add_user_in_db.email, "id": add_user_in_db.id},
        time_exp=ACCESS_TOKEN_EXPIRE_MINUTES
    )


@pytest.fixture
def refresh_token(add_auth_session_in_db: dict):
    return create_token(data={"key": add_auth_session_in_db.get("key")}, time_exp=REFRESH_TOKEN_EXPIRE_MINUTES)


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


@pytest.fixture
def add_conversation_in_db(add_document_in_db, session):

    session.add(
        Conversations(
            user_id=add_document_in_db.user_id,
            document_id=add_document_in_db.id,
            title=add_document_in_db.name,
        )
    )
    session.commit()

    conversation = session.scalar(select(Conversations))

    return conversation


@pytest.fixture
def add_messages_in_db(add_conversation_in_db, session):

    session.add_all(
        [
            Messages(
                conversation_id=add_conversation_in_db.id,
                role="user",
                content="Test question",
            ),
            Messages(
                conversation_id=add_conversation_in_db.id,
                role="assistant",
                content="Test answer",
            ),
        ]
    )
    session.commit()

    messages = session.scalars(
        select(Messages)
        .where(Messages.conversation_id == add_conversation_in_db.id)
        .order_by(Messages.created_at.asc())
    ).all()

    return messages
