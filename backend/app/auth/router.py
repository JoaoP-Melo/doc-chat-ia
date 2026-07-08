from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import Users
from app.auth.schemas import PrivateUser, PublicUser, RequestLogin
from app.auth.service import get_password_hash, verify_password
from app.core.database import get_db
from app.core.security import create_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/user_registration/", status_code=HTTPStatus.OK, response_model=PublicUser
)
def user_registration(user: PrivateUser, session: Session = Depends(get_db)):

    existing_user = session.scalar(select(Users).where(Users.email == user.email))

    if existing_user.email == user.email:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Email already exists",
        )

    if user.password1 != user.password2:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="The passwords are different.",
        )

    hashed_password = get_password_hash(user.password1)
    new_user = Users(
        username=user.username, email=user.email, password_hash=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {
        "username": new_user.username,
        "email": new_user.email,
    }


@router.post("/user_login/", status_code=HTTPStatus.OK)
def user_login(data: RequestLogin, session: Session = Depends(get_db)):

    existing_user = session.scalar(select(Users).where(Users.email == data.email))

    if existing_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Email not found",
        )

    if not verify_password(data.password, existing_user.password_hash):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect password",
        )

    access_token = create_token(
        data={
            "email": str(existing_user.email),
            "id": str(existing_user.id),
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}
