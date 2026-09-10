import logging

from .base import EmailProvider

logger = logging.getLogger("one_paper_wok.email")


class MockEmailProvider(EmailProvider):
    """Logs the code instead of sending it; the API also echoes it back as `debug_code`."""

    name = "mock"
    exposes_debug_code = True

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send_verification_code(self, to_email: str, code: str, ttl_minutes: int) -> None:
        self.sent.append((to_email, code))
        logger.warning(
            "[mock email] verification code for %s: %s (valid %d min)", to_email, code, ttl_minutes
        )
