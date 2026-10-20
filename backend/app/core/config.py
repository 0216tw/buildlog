import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_ROOT / ".env"
load_dotenv(ENV_FILE, override=False)


class DatabaseConfigurationError(RuntimeError):
    pass


def normalize_database_url(value: str | None, *, allow_sqlite: bool = False) -> str:
    if value is None or not value.strip():
        raise DatabaseConfigurationError(
            "DATABASE_URL이 없습니다. backend/.env에 Supabase Session pooler 연결 주소를 입력해 주세요."
        )

    candidate = value.strip()
    if candidate.startswith("postgres://"):
        candidate = candidate.replace("postgres://", "postgresql://", 1)

    try:
        database_url = make_url(candidate)
    except Exception as error:
        raise DatabaseConfigurationError(
            "DATABASE_URL 형식을 읽을 수 없습니다. Supabase Connect 화면의 Session pooler 주소와 비밀번호 URL 인코딩을 확인해 주세요."
        ) from error

    backend_name = database_url.get_backend_name()
    if backend_name == "sqlite":
        if allow_sqlite:
            return database_url.render_as_string(hide_password=False)
        raise DatabaseConfigurationError(
            "실행용 DATABASE_URL은 PostgreSQL이어야 합니다. SQLite 자동 연결은 지원하지 않습니다."
        )

    if backend_name != "postgresql":
        raise DatabaseConfigurationError(
            "DATABASE_URL은 PostgreSQL 연결 주소여야 합니다."
        )

    if database_url.host is None or database_url.database is None:
        raise DatabaseConfigurationError(
            "DATABASE_URL에 호스트와 데이터베이스 이름이 모두 필요합니다."
        )

    if not allow_sqlite:
        if not database_url.host.endswith(".pooler.supabase.com"):
            raise DatabaseConfigurationError(
                "Supabase Session pooler 호스트를 확인해 주세요. Dashboard의 Connect 화면에서 주소를 복사해야 합니다."
            )
        if database_url.port != 5432:
            raise DatabaseConfigurationError(
                "Session pooler 포트는 5432입니다. Transaction pooler의 6543 포트를 사용하지 마세요."
            )

    database_url = database_url.set(drivername="postgresql+psycopg")
    if "sslmode" not in database_url.query:
        database_url = database_url.update_query_dict({"sslmode": "require"})
    if "connect_timeout" not in database_url.query:
        database_url = database_url.update_query_dict({"connect_timeout": "10"})
    return database_url.render_as_string(hide_password=False)


@dataclass(frozen=True)
class Settings:
    app_name: str = "BuildLog API"
    api_prefix: str = "/api"
    environment: str = os.getenv("BUILDLOG_ENV", "development")
    database_url: str = normalize_database_url(
        os.getenv("DATABASE_URL"),
        allow_sqlite=os.getenv("BUILDLOG_ENV") == "test",
    )
    frontend_origin: str = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )
    session_cookie_name: str = "buildlog_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 7
    session_cookie_secure: bool = os.getenv(
        "SESSION_COOKIE_SECURE",
        "false",
    ).lower() == "true"
    openai_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "").strip() or None,
        repr=False,
    )


settings = Settings()
