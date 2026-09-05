from abc import ABC, abstractmethod


class EmailProvider(ABC):
    """Sends transactional email. Implementations must be safe to call from a request handler."""

    name: str = "base"
    exposes_debug_code: bool = False

    @abstractmethod
    async def send_verification_code(self, to_email: str, code: str, ttl_minutes: int) -> None: ...
