from datetime import datetime
import hashlib
from http import HTTPStatus
import os
import secrets

from dotenv import load_dotenv
from fastapi import HTTPException, Response
from jwt import decode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import AuthSessions, Users
from app.auth.schemas import FormRegister, RequestLogin
from app.core.security import create_token

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = 15
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
pwd_context = PasswordHash.recommended()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def validate_user_registration_credentials(user: FormRegister, session: Session):

    user_in_db = session.scalar(select(Users).where(Users.email == user.email))

    if user_in_db:
        if user_in_db.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    if user.password1 != user.password2:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Passwords do not match",
        )


def add_user_in_db(user: FormRegister, session: Session):

    hashed_password = get_password_hash(user.password1)
    new_user = Users(
        username=user.username, email=user.email, password_hash=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)


def validate_user_login_credentials(data: RequestLogin, session: Session):

    user_in_db = session.scalar(select(Users).where(Users.email == data.email))

    if user_in_db is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, user_in_db.password_hash):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {
        "id": user_in_db.id,
        "username": user_in_db.username,
        "email": user_in_db.email,
    }


def create_refresh_token(user_email, session: Session):

    key = secrets.token_urlsafe(64)
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    refresh_token = create_token(data={"key": key})

    user_in_db = session.scalar(select(Users).where(Users.email == user_email))

    new_session = AuthSessions(
        user_id=user_in_db.id,
        refresh_token_hash=key_hash,
    )

    session.add(new_session)
    session.commit()
    session.refresh(new_session)

    return refresh_token


def set_cookies(response: Response, access_token, refresh_token):

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
    )


def decode_access_token(access_token):

    if not access_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, 
            detail="Access token not found"
        )

    payload = decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    subject_id = payload.get("id")
    subject_email = payload.get("email")

    return subject_id, subject_email


def decode_refresh_token(refresh_token):

    if not refresh_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, 
            detail="Token not found"
        )

    payload = decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

    subject_key = payload.get("key")
    subject_key_hash = hashlib.sha256(subject_key.encode()).hexdigest()

    return subject_key_hash


def validate_user_session(key_hash, session: Session, response: Response):

    existing_session = session.scalar(
        select(AuthSessions).where(
            AuthSessions.refresh_token_hash == key_hash,
        )
    )

    if existing_session:
        if existing_session.revoked == True:
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, 
                detail="Token revoked"
            )

        if existing_session.expires_at <= datetime.now():
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, 
                detail="Token expired"
            )
    else:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, 
            detail="Invalid token"
        )

    return existing_session.user_id


def update_refresh_token(key_hash, user_id, session):

    new_key = secrets.token_urlsafe(64)
    new_key_hash = hashlib.sha256(new_key.encode()).hexdigest()

    refresh_token = create_token(data={"key": new_key})

    session_in_db = session.scalar(
        select(AuthSessions).where(
            AuthSessions.refresh_token_hash == key_hash,
            AuthSessions.user_id == int(user_id),
        )
    )

    session_in_db.refresh_token_hash = new_key_hash

    session.commit()
    session.refresh(session_in_db)

    return refresh_token


def delete_user_session(key_hash, user_id, session: Session):

    current_session = session.scalar(
        select(AuthSessions).where(
            AuthSessions.refresh_token_hash == key_hash,
            AuthSessions.user_id == int(user_id),
        )
    )

    session.delete(current_session)
    session.commit()
