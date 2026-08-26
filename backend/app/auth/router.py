from http import HTTPStatus
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Cookie, Depends, Response, Request
from sqlalchemy.orm import Session

from app.auth.schemas import FormRegister, PublicUser, RequestLogin
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
from app.core.limiter import limiter

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 15
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register/", status_code=HTTPStatus.CREATED, response_model=PublicUser
)
@limiter.limit("60/minute")
def user_registration(
    request: Request,
    user: FormRegister, 
    session: Session = Depends(get_db)):

    validate_user_registration_credentials(user, session)
    add_user_in_db(user, session)

    return {
        "username": user.username,
        "email": user.email,
    }


@router.post("/login/", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def user_login(
    request: Request,
    data: RequestLogin, response: Response, 
    session: Session = Depends(get_db)
):

    user_validated = validate_user_login_credentials(data, session)

    access_token = create_token(
        data={"id": user_validated["id"]},
        time_exp=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = create_refresh_token(data.email, session)

    set_cookies(response, access_token, refresh_token)



@router.post("/refresh/", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def refresh_token(
    request: Request,
    response: Response, 
    session: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    
    subject_key_hash = decode_refresh_token(refresh_token)

    subject_id = validate_user_session(subject_key_hash, session, response)

    access_token = create_token(
        data={"id": subject_id},
        time_exp=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    refresh_token = update_refresh_token(subject_key_hash, subject_id, session)

    set_cookies(response, access_token, refresh_token)



@router.delete("/logout/", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def logout_user(
    request: Request,
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
