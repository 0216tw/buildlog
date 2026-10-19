from pydantic import BaseModel, field_validator

from app.schemas.validators import normalize_email, normalize_nickname, validate_password


class SignupRequest(BaseModel):
    email: str
    password: str
    nickname: str

    _normalize_email = field_validator("email")(normalize_email)
    _validate_password = field_validator("password")(validate_password)
    _normalize_nickname = field_validator("nickname")(normalize_nickname)


class LoginRequest(BaseModel):
    email: str
    password: str

    _normalize_email = field_validator("email")(normalize_email)
