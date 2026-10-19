from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.validators import normalize_nickname


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nickname: str
    is_admin: bool


class NicknameUpdateRequest(BaseModel):
    nickname: str

    _normalize_nickname = field_validator("nickname")(normalize_nickname)
