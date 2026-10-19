from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import Pool, StaticPool

from app.core.config import settings


def create_database_engine(
    database_url: str,
    *,
    poolclass: type[Pool] | None = None,
) -> Engine:
    options: dict[str, object] = {}

    if database_url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
        if database_url.endswith(":memory:") or database_url in {"sqlite://", "sqlite+pysqlite://"}:
            options["poolclass"] = StaticPool
    else:
        options.update(
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
            pool_recycle=1800,
        )

    if poolclass is not None:
        options["poolclass"] = poolclass
        options.pop("pool_size", None)
        options.pop("max_overflow", None)
        options.pop("pool_recycle", None)

    database_engine = create_engine(database_url, **options)

    if database_url.startswith("sqlite"):
        @event.listens_for(database_engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return database_engine


class Base(DeclarativeBase):
    pass


engine = create_database_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
