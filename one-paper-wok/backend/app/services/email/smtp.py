from email.message import EmailMessage

import aiosmtplib

from ...config import Settings
from .base import EmailProvider


class SmtpEmailProvider(EmailProvider):
    name = "smtp"

    def __init__(self, settings: Settings) -> None:
        if not settings.smtp_host or not settings.smtp_from:
            raise ValueError("SMTP_HOST and SMTP_FROM are required for the smtp email provider")
        self._settings = settings

    async def send_verification_code(self, to_email: str, code: str, ttl_minutes: int) -> None:
        s = self._settings
        msg = EmailMessage()
        msg["From"] = s.smtp_from
        msg["To"] = to_email
        msg["Subject"] = f"【一纸读书煲】登录验证码 {code}"
        msg.set_content(
            f"你的登录验证码是：{code}\n\n{ttl_minutes} 分钟内有效。如果这不是你的操作，请忽略本邮件。\n\n— 一纸读书煲 One Paper Wok"
        )
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password,
            use_tls=s.smtp_use_tls,
        )
