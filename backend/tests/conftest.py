import os

import pytest


test_database_url = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
if not test_database_url.startswith("sqlite"):
    raise RuntimeError("자동 테스트는 SQLite3 데이터베이스만 사용할 수 있습니다.")
os.environ["BUILDLOG_ENV"] = "test"
os.environ["DATABASE_URL"] = test_database_url

from app import models  # noqa: E402,F401
from app.db.database import Base, engine  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
