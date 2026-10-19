from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.records import strip_required


RecordType = Literal["study", "error"]
ReportTargetType = Literal["study", "todo", "error", "comment"]


class CommentWrite(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return strip_required(value, label="댓글", maximum=500)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    author_nickname: str
    content: str
    created_at: datetime
    updated_at: datetime


class LikeResponse(BaseModel):
    liked: bool
    count: int


class ReportCreate(BaseModel):
    target_type: ReportTargetType
    target_id: int
    reason: str

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return strip_required(value, label="신고 이유", maximum=500)


class ReportResponse(BaseModel):
    id: int
    target_type: ReportTargetType
    target_id: int
    reporter_id: int
    reporter_nickname: str
    reason: str
    created_at: datetime
