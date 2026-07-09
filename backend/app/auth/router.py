from http import HTTPStatus
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.auth.schemas import PrivateUser, PublicUser, RequestLogin
from app.auth.service import (
    add_user_in_db,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    delete_user_session,
    set_cookies,
    update_refresh_token,
    validate_user_login_credentials,
    validate_user_registration_credentials,
    validate_user_session,
)
from app.core.database import get_db
from app.core.security import create_token

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 15
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/user_registration/", status_code=HTTPStatus.OK, response_model=PublicUser
)
def user_registration(user: PrivateUser, session: Session = Depends(get_db)):

    validate_user_registration_credentials(user, session)
    add_user_in_db(user, session)

    return {
        "username": user.username,
        "email": user.email,
    }


@router.post("/user_login/", status_code=HTTPStatus.OK)
def user_login(
    data: RequestLogin, response: Response, session: Session = Depends(get_db)
):

    user_validated = validate_user_login_credentials(data, session)

    access_token = create_token(
        data={"email": user_validated["email"], "id": user_validated["id"]}
    )
    refresh_token = create_refresh_token(data.email, session)

    set_cookies(response, access_token, refresh_token)

    """excluir session caso exista e criar outra"""

    return {"Message": "Login successful"}


@router.post("/refresh_token/", status_code=HTTPStatus.OK)
def refresh_token(
    response: Response,
    session: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None),
    refresh_token: str | None = Cookie(default=None),
):

    subject_id, subject_email = decode_access_token(access_token)
    subject_key_hash = decode_refresh_token(refresh_token)

    validate_user_session(subject_id, subject_key_hash, session, response)

    access_token = create_token(
        data={
            "email": subject_email,
            "id": subject_id,
        }
    )
    refresh_token = update_refresh_token(subject_key_hash, subject_id, session)

    set_cookies(response, access_token, refresh_token)

    return {"Message": "Token updated"}


@router.delete("/user_logout/", status_code=HTTPStatus.OK)
def logout_user(
    response: Response,
    session: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None),
    refresh_token: str | None = Cookie(default=None),
):

    subject_id, subject_email = decode_access_token(access_token)
    subject_key_hash = decode_refresh_token(refresh_token)

    delete_user_session(subject_key_hash, subject_id, session)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"Message": "Logout successful"}
