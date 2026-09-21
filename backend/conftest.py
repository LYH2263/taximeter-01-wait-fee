import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="taxitest_")

import pytest
from fastapi.testclient import TestClient

from app.db import DB_PATH
from app.main import app


@pytest.fixture()
def client():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with TestClient(app) as c:
        yield c
