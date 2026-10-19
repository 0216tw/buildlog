from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


def strip_required(value: str, *, label: str, maximum: int) -> str:
    candidate = value.strip()
    if not candidate:
        raise ValueError(f"{label}을(를) 입력해 주세요.")
    if len(candidate) > maximum:
        raise ValueError(f"{label}은(는) {maximum}자 이하로 입력해 주세요.")
    return candidate


def strip_optional(value: str | None, *, label: str, maximum: int) -> str | None:
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    if len(candidate) > maximum:
        raise ValueError(f"{label}은(는) {maximum}자 이하로 입력해 주세요.")
    return candidate


class VisibilityUpdate(BaseModel):
    is_public: bool


class StudyWrite(BaseModel):
    title: str
    content: str
    is_public: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_required(value, label="제목", maximum=100)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return strip_required(value, label="내용", maximum=5000)


class StudyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    content: str
    is_public: bool
    created_at: datetime
    updated_at: datetime


class TodoWrite(BaseModel):
    title: str
    is_public: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_required(value, label="제목", maximum=100)


class TodoCompletionUpdate(BaseModel):
    is_completed: bool


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    is_completed: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ErrorWrite(BaseModel):
    title: str
    content: str
    resolution: str | None = None
    is_resolved: bool = False
    is_public: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_required(value, label="오류 제목", maximum=100)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return strip_required(value, label="오류 내용", maximum=5000)

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, value: str | None) -> str | None:
        return strip_optional(value, label="해결 방법", maximum=5000)

    @model_validator(mode="after")
    def require_resolution_when_resolved(self):
        if self.is_resolved and not self.resolution:
            raise ValueError("해결 상태로 저장하려면 해결 방법을 입력해 주세요.")
        return self


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    content: str
    resolution: str | None
    is_resolved: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class PublicRecordResponse(BaseModel):
    type: Literal["study", "todo", "error"]
    id: int
    title: str
    content: str | None = None
    status: str | None = None
    author_nickname: str
    created_at: datetime
    updated_at: datetime
