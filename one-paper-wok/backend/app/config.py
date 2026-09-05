import os
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_JWT_SECRETS = frozenset({"", "dev-only-change-me", "change-me", "secret"})
_DEFAULT_DATABASE_URL = "sqlite:///./data/app.db"
_DEFAULT_DATA_DIR = Path("data")


def _sqlite_url(db_file: Path) -> str:
    return "sqlite:///" + db_file.as_posix()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "One Paper Wok"
    database_url: str = _DEFAULT_DATABASE_URL
    data_dir: Path = _DEFAULT_DATA_DIR

    # Auth
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 120
    refresh_token_days: int = 30
    email_code_ttl_minutes: int = 10
    email_code_resend_seconds: int = 60
    email_code_max_attempts: int = 5

    # Providers: "auto" picks the real provider when credentials exist, otherwise mock.
    ocr_provider: str = "auto"
    llm_provider: str = "auto"
    email_provider: str = "auto"

    # Baidu OCR
    baidu_ocr_api_key: str | None = None
    baidu_ocr_secret_key: str | None = None

    # Qwen (DashScope OpenAI-compatible)
    dashscope_api_key: str | None = None
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"

    # SMTP
    smtp_host: str | None = None
    smtp_port: int = 465
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True

    # Image preprocessing
    max_image_side: int = 1600

    @model_validator(mode="after")
    def apply_volume_defaults(self):
        volume = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")
        if not volume:
            return self
        volume_path = Path(volume)
        if self.data_dir == _DEFAULT_DATA_DIR:
            self.data_dir = volume_path
        if self.database_url == _DEFAULT_DATABASE_URL:
            self.database_url = _sqlite_url(volume_path / "app.db")
        return self

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    def hosted_on_railway(self) -> bool:
        return bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"))

    def jwt_secret_is_insecure(self) -> bool:
        return self.jwt_secret.strip().lower() in _INSECURE_JWT_SECRETS

    def resolved_ocr_provider(self) -> str:
        if self.ocr_provider != "auto":
            return self.ocr_provider
        return "baidu" if self.baidu_ocr_api_key and self.baidu_ocr_secret_key else "mock"

    def resolved_llm_provider(self) -> str:
        if self.llm_provider != "auto":
            return self.llm_provider
        return "qwen" if self.dashscope_api_key else "mock"

    def resolved_email_provider(self) -> str:
        if self.email_provider != "auto":
            return self.email_provider
        return "smtp" if self.smtp_host and self.smtp_from else "mock"


def require_secure_jwt_if_hosted(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if settings.hosted_on_railway() and settings.jwt_secret_is_insecure():
        raise RuntimeError("Railway 部署必须设置 JWT_SECRET，不要使用默认值。")


@lru_cache
def get_settings() -> Settings:
    return Settings()
