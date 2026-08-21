from datetime import UTC, datetime, timedelta
from http import HTTPStatus
import os

from dotenv import load_dotenv
from fastapi import Cookie, Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
)
from jwt import DecodeError, decode, encode
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import Users
from app.core.database import get_db

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 15
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = HTTPBearer()


def create_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(
    access_token: str | None = Cookie(default=None), session: Session = Depends(get_db)
):
    try:
        payload = decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_id = payload.get("id")

        if not subject_id:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, 
                detail="Could not validate credentials"
            )

    except DecodeError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, 
            detail="Could not validate credentials"
        )

    current_user = session.scalar(select(Users).where(Users.id == subject_id))

    if not current_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return current_user
