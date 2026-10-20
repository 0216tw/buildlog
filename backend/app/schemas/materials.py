from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.records import strip_required


class MaterialText(BaseModel):
    title: str
    memo: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_required(value, label="자료 제목", maximum=100)

    @field_validator("memo")
    @classmethod
    def validate_memo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        candidate = value.strip()
        if not candidate:
            return None
        if len(candidate) > 1000:
            raise ValueError("메모는 1,000자 이하로 입력해 주세요.")
        return candidate


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    memo: str | None
    original_filename: str
    media_type: str
    content_type: str
    size_bytes: int
    ai_summary: str | None
    ai_status: Literal["not_requested", "pending", "processing", "completed", "failed"]
    ai_analyzed_at: datetime | None
    created_at: datetime
