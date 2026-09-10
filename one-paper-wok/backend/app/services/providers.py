"""Provider registry. Real providers are used when credentials exist, otherwise mocks."""

from functools import lru_cache

from ..config import get_settings
from .email.base import EmailProvider
from .email.mock import MockEmailProvider
from .llm.base import LlmProvider
from .llm.mock import MockLlmProvider
from .ocr.base import OcrProvider
from .ocr.mock import MockOcrProvider


@lru_cache
def get_ocr_provider() -> OcrProvider:
    settings = get_settings()
    if settings.resolved_ocr_provider() == "baidu":
        from .ocr.baidu import BaiduOcrProvider

        return BaiduOcrProvider(settings)
    return MockOcrProvider()


@lru_cache
def get_llm_provider() -> LlmProvider:
    settings = get_settings()
    if settings.resolved_llm_provider() == "qwen":
        from .llm.qwen import QwenLlmProvider

        return QwenLlmProvider(settings)
    return MockLlmProvider()


@lru_cache
def get_email_provider() -> EmailProvider:
    settings = get_settings()
    if settings.resolved_email_provider() == "smtp":
        from .email.smtp import SmtpEmailProvider

        return SmtpEmailProvider(settings)
    return MockEmailProvider()


def reset_providers() -> None:
    get_ocr_provider.cache_clear()
    get_llm_provider.cache_clear()
    get_email_provider.cache_clear()
