from pydantic import BaseModel, EmailStr, field_validator
import re

class FormRegister(BaseModel):
    username: str
    email: str
    password1: str
    password2: str

    @field_validator("password1")
    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("The password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", password):
            raise ValueError("The password must contain an uppercase letter.")

        if not re.search(r"[a-z]", password):
            raise ValueError("The password must contain a lowercase letter.")

        if not re.search(r"\d", password):
            raise ValueError("The password must contain a number.")

        return password



class PublicUser(BaseModel):
    username: str
    email: EmailStr


class RequestLogin(BaseModel):
    email: EmailStr
    password: str
