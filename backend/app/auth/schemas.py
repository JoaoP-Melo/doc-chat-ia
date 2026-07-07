from pydantic import BaseModel, EmailStr


class PrivateUser(BaseModel):
    username: str
    email: EmailStr
    password1: str
    password2: str


class PublicUser(BaseModel):
    username: str
    email: EmailStr
