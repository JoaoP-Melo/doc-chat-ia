from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.schemas import PrivateUser, PublicUser
from app.auth.models import Users
from app.core.database import get_db
from app.auth.security import get_password_hash

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/user_registration/", status_code=HTTPStatus.OK, response_model=PublicUser
)
def user_registration(user: PrivateUser, session: Session = Depends(get_db)):

    existing_user = session.scalar(select(Users).where((Users.email == user.email)))

    if existing_user:
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
