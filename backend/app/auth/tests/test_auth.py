from fastapi.testclient import TestClient
from http import HTTPStatus
from app.main import app
from sqlalchemy import select
from app.auth.models import Users


client = TestClient(app)

def test_user_registration_succes(client_override, session):
    
    user_data = {
            'username': 'testtest',
            'email': 'test@example.com',
            'password1': 'testtest',
            'password2': 'testtest'
        }
    
    response = client.post(
        'auth/user_registration/',
        json=user_data
    )

    assert response.status_code == HTTPStatus.CREATED

    users_in_db = session.scalar(
        select(Users).where(Users.email == user_data["email"])
        )

    assert users_in_db is not None
    assert users_in_db.email == user_data["email"]


def test_user_registration_email_conflict(client_override, session, add_user_in_db):
    
    user_data = {
            'username': 'testtest',
            'email': 'test@example.com',
            'password1': 'testtest',
            'password2': 'testtest'
        }
    
    response = client.post(
        'auth/user_registration/',
        json=user_data
    )

    assert response.status_code == HTTPStatus.CONFLICT

    users_in_db = session.scalars(
        select(Users).where(Users.email == user_data["email"])
        ).all()
    
    assert len(users_in_db) == 1




def test_user_registration_different_password(client_override, session):

    user_data = {
            'username': 'testtest',
            'email': 'test@example.com',
            'password1': 'testtest',
            'password2': 'test'
        }
    
    response = client.post(
        'auth/user_registration/',
        json=user_data
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    users_in_db = session.scalar(
        select(Users).where(Users.email == user_data["email"])
        )
    
    assert users_in_db is None


def test_user_login_success(client_override, session, add_user_in_db):
    user_data = {
        'email':'test@example.com',
        'password': 'testtest'
    }

    response = client_override.post(
        'auth/user_login/',
        json=user_data
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.cookies
    assert 'refresh_token' in response.cookies

    auth_sessions_in_db = session.scalars(
        select(Users)
        ).all()
    
    assert len(auth_sessions_in_db) == 1

def test_user_login_email_not_found(client_override, session, add_user_in_db):
    user_data = {
        'email':'testtest@example.com',
        'password': 'testtest'
    }

    response = client_override.post(
        'auth/user_login/',
        json=user_data
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'access_token' not in response.cookies
    assert 'refresh_token' not in response.cookies


def test_user_login_incorrect_password(client_override, session, add_user_in_db):
    user_data = {
        'email':'test@example.com',
        'password': 'test'
    }

    response = client_override.post(
        'auth/user_login/',
        json=user_data
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'access_token' not in response.cookies
    assert 'refresh_token' not in response.cookies
