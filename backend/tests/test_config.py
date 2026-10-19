import pytest

from app.core.config import DatabaseConfigurationError, normalize_database_url


def test_database_url_is_required_for_runtime() -> None:
    with pytest.raises(DatabaseConfigurationError, match="DATABASE_URL이 없습니다"):
        normalize_database_url(None)


def test_runtime_does_not_fall_back_to_sqlite() -> None:
    with pytest.raises(DatabaseConfigurationError, match="SQLite 자동 연결은 지원하지 않습니다"):
        normalize_database_url("sqlite:///buildlog.sqlite3")


def test_session_pooler_port_must_be_5432() -> None:
    with pytest.raises(DatabaseConfigurationError, match="Session pooler 포트는 5432"):
        normalize_database_url(
            "postgresql://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres"
        )


def test_supabase_session_pooler_url_uses_psycopg_and_ssl() -> None:
    result = normalize_database_url(
        "postgresql://postgres.project:password@aws-0-region.pooler.supabase.com:5432/postgres"
    )

    assert result.startswith("postgresql+psycopg://")
    assert "sslmode=require" in result
    assert "connect_timeout=10" in result


def test_sqlite_is_allowed_only_for_explicit_tests() -> None:
    result = normalize_database_url(
        "sqlite+pysqlite:///:memory:",
        allow_sqlite=True,
    )

    assert result == "sqlite+pysqlite:///:memory:"
