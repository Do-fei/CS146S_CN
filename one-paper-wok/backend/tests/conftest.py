import io
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import get_settings
from app.db import get_engine, reset_engine
from app.models import Base
from app.services.providers import reset_providers


def _tiny_jpeg(color: tuple[int, int, int] = (240, 200, 160)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (320, 240), color).save(buf, format="JPEG", quality=80)
    return buf.getvalue()


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("OCR_PROVIDER", "mock")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("EMAIL_PROVIDER", "mock")
    get_settings.cache_clear()
    reset_engine()
    reset_providers()
    Base.metadata.create_all(bind=get_engine())

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    reset_engine()
    get_settings.cache_clear()
    reset_providers()


@pytest.fixture()
def jpeg_bytes() -> bytes:
    return _tiny_jpeg()


def auth_headers(client: TestClient, email: str = "reader@example.com") -> dict[str, str]:
    send = client.post("/auth/send-code", json={"email": email})
    assert send.status_code == 200, send.text
    code = send.json()["debug_code"]
    assert code
    verify = client.post(
        "/auth/verify",
        json={"email": email, "code": code, "device_id": "pytest-device"},
    )
    assert verify.status_code == 200, verify.text
    return {"Authorization": f"Bearer {verify.json()['access_token']}"}
