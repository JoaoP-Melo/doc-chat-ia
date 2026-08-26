from datetime import datetime
from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import AuthSessions, Users
from app.main import app

client = TestClient(app)


def test_user_registration_succes(client_override, session):

    user_data = {
        "username": "testtest",
        "email": "test@example.com",
        "password1": "Testtest1",
        "password2": "Testtest1",
    }

    response = client_override.post("auth/register/", json=user_data)

    assert response.status_code == HTTPStatus.CREATED

    users_in_db = session.scalar(select(Users).where(Users.email == user_data["email"]))
    response_data = response.json()

    assert response_data == {
        "username": user_data["username"],
        "email": user_data["email"],
    }
    assert users_in_db is not None
    assert users_in_db.email == user_data["email"]


def test_user_registration_rejects_existing_email(
    client_override, session, add_user_in_db
):

    user_data = {
        "username": "testtest",
        "email": "test@example.com",
        "password1": "Testtest1",
        "password2": "Testtest1",
    }

    response = client_override.post("auth/register/", json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Email already exists"}

    users_in_db = session.scalars(
        select(Users).where(Users.email == user_data["email"])
    ).all()

    assert len(users_in_db) == 1


def test_user_registration_rejects_different_passwords(client_override, session):

    user_data = {
        "username": "testtest",
        "email": "test@example.com",
        "password1": "Testtest1",
        "password2": "Different1",
    }

    response = client_override.post("auth/register/", json=user_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Passwords do not match"}

    users_in_db = session.scalar(select(Users).where(Users.email == user_data["email"]))

    assert users_in_db is None


def test_user_login_success(client_override, session, add_user_in_db):
    user_data = {"email": "test@example.com", "password": "testtest"}

    response = client_override.post("auth/login/", json=user_data)

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    auth_sessions_in_db = session.scalars(select(Users)).all()

    assert len(auth_sessions_in_db) == 1


def test_user_login_rejects_unknown_email(client_override, session, add_user_in_db):
    user_data = {"email": "testtest@example.com", "password": "testtest"}

    response = client_override.post("auth/login/", json=user_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid email or password"}
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


def test_user_login_incorrect_password(client_override, session, add_user_in_db):
    user_data = {"email": "test@example.com", "password": "test"}

    response = client_override.post("auth/login/", json=user_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid email or password"}
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


def test_refresh_token_success(client_override, refresh_token):

    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.post("auth/refresh/")

    assert response.status_code == HTTPStatus.OK
    assert response.cookies.get("access_token")
    assert response.cookies.get("refresh_token") != refresh_token


def test_refresh_token_rejects_unknown_session(client_override, session, refresh_token):

    auth_session_in_db = session.scalar(select(AuthSessions))
    session.delete(auth_session_in_db)
    session.commit()

    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.post("auth/refresh/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_refresh_token_rejects_malformed_token(client_override):

    client_override.cookies.set("refresh_token", "malformed-token")
    response = client_override.post("auth/refresh/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_refresh_token_rejects_missing_token(client_override):

    response = client_override.post("auth/refresh/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Token not found"}


def test_refresh_token_rejects_revoked_session(client_override, session, refresh_token):

    auth_session_in_db = session.scalar(select(AuthSessions))

    auth_session_in_db.revoked = True

    session.commit()

    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.post("auth/refresh/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Token revoked"}


def test_refresh_token_rejects_expired_session(client_override, session, refresh_token):

    auth_session_in_db = session.scalar(select(AuthSessions))

    auth_session_in_db.expires_at = datetime.now()

    session.commit()

    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.post("auth/refresh/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Token expired"}


def test_logout_user_success(client_override, session, access_token, refresh_token):

    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.delete("auth/logout/")

    auth_sessions_in_db = session.scalars(select(AuthSessions)).all()
    deleted_cookies = response.headers.get_list("set-cookie")

    assert response.status_code == HTTPStatus.OK
    assert len(auth_sessions_in_db) == 0
    assert any(
        cookie.startswith("access_token=") and "Max-Age=0" in cookie
        for cookie in deleted_cookies
    )
    assert any(
        cookie.startswith("refresh_token=") and "Max-Age=0" in cookie
        for cookie in deleted_cookies
    )


def test_logout_user_access_token_not_found(client_override, session, refresh_token):

    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.delete("auth/user_logout/")

    auth_sessions_in_db = session.scalars(select(AuthSessions)).all()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies


def test_logout_user_refresh_token_not_found(
    client_override,
    session,
    access_token,
):

    client_override.cookies.set("access_token", access_token)
    response = client_override.delete("auth/user_logout/")

    auth_sessions_in_db = session.scalars(select(AuthSessions)).all()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies
    assert len(auth_sessions_in_db) == 0
