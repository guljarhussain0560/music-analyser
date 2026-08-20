import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import httpx

# Compatibility shim for starlette TestClient across httpx versions (<0.20 and >=0.20)
if not hasattr(httpx.Client, "_orig_init"):
    _orig_init = httpx.Client.__init__

    def _patched_init(self, *args, **kwargs):
        if "follow_redirects" in kwargs:
            # Map follow_redirects to allow_redirects if running under older httpx
            import inspect

            sig = inspect.signature(_orig_init)
            if "follow_redirects" not in sig.parameters and "allow_redirects" in sig.parameters:
                kwargs["allow_redirects"] = kwargs.pop("follow_redirects")
        return _orig_init(self, *args, **kwargs)

    httpx.Client._orig_init = _orig_init
    httpx.Client.__init__ = _patched_init

import tempfile
from collections.abc import Generator

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.models import User
from app.main import app

# In-memory SQLite database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    settings.APP_ENV = "test"
    settings.SECRET_KEY = "test-secret-key-for-unit-testing-purposes-only-32bytes"
    settings.ALGORITHM = "HS256"
    settings.AWS_S3_BUCKET_NAME = ""
    settings.GROQ_API_KEY = ""


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        name="Test Artist",
        username="testartist",
        email="artist@example.com",
        hashed_password=get_password_hash("SecretPassword123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_wav_file() -> Generator[str, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sr = 22050
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        audio_data = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.25 * np.sin(2 * np.pi * 880 * t)
        sf.write(tmp.name, audio_data, sr, subtype="PCM_16")
        tmp_path = tmp.name

    yield tmp_path

    if os.path.exists(tmp_path):
        os.remove(tmp_path)
