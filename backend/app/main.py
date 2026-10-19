from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api import auth, errors, interactions, public_records, reports, studies, todos, users
from app.core.config import settings


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(studies.router, prefix=settings.api_prefix)
app.include_router(todos.router, prefix=settings.api_prefix)
app.include_router(errors.router, prefix=settings.api_prefix)
app.include_router(public_records.router, prefix=settings.api_prefix)
app.include_router(interactions.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    first_error = error.errors()[0] if error.errors() else {}
    message = str(first_error.get("msg", "입력값을 확인해 주세요."))
    if message.startswith("Value error, "):
        message = message.removeprefix("Value error, ")
    elif first_error.get("type") == "missing":
        message = "필수 입력값을 모두 입력해 주세요."
    return JSONResponse(status_code=422, content={"detail": message})


@app.exception_handler(Exception)
async def unexpected_exception_handler(_request: Request, _error: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "서버에서 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."},
    )


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="buildlog-api")
