from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "One Paper Wok"
    database_url: str = "sqlite:///./data/app.db"
    data_dir: Path = Path("data")

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

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
