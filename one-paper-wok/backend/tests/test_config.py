from pathlib import Path

import pytest

from app.config import Settings, get_settings, require_secure_jwt_if_hosted


def test_railway_volume_rewrites_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RAILWAY_VOLUME_MOUNT_PATH", str(tmp_path))
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()
    settings = Settings()
    assert settings.data_dir == tmp_path
    assert settings.database_url == f"sqlite:///{(tmp_path / 'app.db').as_posix()}"
    assert settings.uploads_dir == tmp_path / "uploads"


def test_explicit_database_url_wins_over_volume(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RAILWAY_VOLUME_MOUNT_PATH", str(tmp_path))
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.delenv("DATA_DIR", raising=False)
    settings = Settings()
    assert settings.database_url == "sqlite:///:memory:"
    assert settings.data_dir == tmp_path


def test_railway_rejects_default_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    settings = Settings()
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        require_secure_jwt_if_hosted(settings)


def test_local_dev_allows_default_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.delenv("RAILWAY_PROJECT_ID", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    require_secure_jwt_if_hosted(Settings())
