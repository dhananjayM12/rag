import os
import tempfile

# Point the app at a throwaway SQLite DB BEFORE importing any app module,
# so config/engine pick it up. The Embedding column degrades to text on SQLite.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import syllabus_seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    syllabus_seed.run()
    yield
    os.close(_db_fd)
    os.remove(_db_path)


@pytest.fixture()
def client():
    return TestClient(app)
