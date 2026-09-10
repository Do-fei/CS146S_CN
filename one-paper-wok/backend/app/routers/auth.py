from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..auth.jwt import (
    create_access_token,
    generate_code,
    generate_refresh_token,
    hash_token,
)
from ..config import get_settings
from ..db import get_db
from ..models import EmailCode, RefreshToken, User, utcnow
from ..schemas import (
    LogoutRequest,
    RefreshRequest,
    SendCodeRequest,
    SendCodeResponse,
    TokenPair,
    UserOut,
    VerifyCodeRequest,
)
from ..services.providers import get_email_provider

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(db: Session, user: User, device_id: str) -> TokenPair:
    settings = get_settings()
    access, expires_in = create_access_token(user.id)
    raw_refresh = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            device_id=device_id,
            expires_at=utcnow() + timedelta(days=settings.refresh_token_days),
        )
    )
    db.commit()
    return TokenPair(access_token=access, refresh_token=raw_refresh, expires_in=expires_in)


@router.post("/send-code", response_model=SendCodeResponse)
async def send_code(payload: SendCodeRequest, db: Session = Depends(get_db)) -> SendCodeResponse:
    settings = get_settings()
    email = payload.email.lower()
    latest = db.scalars(
        select(EmailCode)
        .where(EmailCode.email == email)
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    ).first()
    now = utcnow()
    if latest is not None:
        elapsed = (now - latest.created_at).total_seconds()
        if elapsed < settings.email_code_resend_seconds:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"请 {int(settings.email_code_resend_seconds - elapsed)} 秒后再试",
            )

    code = generate_code()
    db.add(
        EmailCode(
            email=email,
            code_hash=hash_token(code),
            expires_at=now + timedelta(minutes=settings.email_code_ttl_minutes),
        )
    )
    db.commit()

    provider = get_email_provider()
    try:
        await provider.send_verification_code(email, code, settings.email_code_ttl_minutes)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"验证码发送失败: {exc}") from exc

    return SendCodeResponse(
        resend_after_seconds=settings.email_code_resend_seconds,
        debug_code=code if provider.exposes_debug_code else None,
    )


@router.post("/verify", response_model=TokenPair)
def verify_code(payload: VerifyCodeRequest, db: Session = Depends(get_db)) -> TokenPair:
    settings = get_settings()
    email = payload.email.lower()
    record = db.scalars(
        select(EmailCode)
        .where(EmailCode.email == email, EmailCode.consumed.is_(False))
        .order_by(EmailCode.created_at.desc())
        .limit(1)
    ).first()
    if record is None or record.expires_at < utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "验证码已过期，请重新获取")
    if record.attempts >= settings.email_code_max_attempts:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "尝试次数过多，请重新获取验证码")
    if record.code_hash != hash_token(payload.code):
        record.attempts += 1
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "验证码错误")

    record.consumed = True
    user = db.scalars(select(User).where(User.email == email)).first()
    if user is None:
        user = User(email=email)
        db.add(user)
        db.flush()
    return _issue_tokens(db, user, payload.device_id)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    token = db.scalars(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(payload.refresh_token))
    ).first()
    if token is None or token.revoked or token.expires_at < utcnow():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "刷新令牌无效，请重新登录")
    user = db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")
    token.revoked = True  # rotate: each refresh token can only be used once
    return _issue_tokens(db, user, token.device_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> None:
    token = db.scalars(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(payload.refresh_token))
    ).first()
    if token is not None:
        token.revoked = True
        db.commit()


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=user.id, email=user.email, created_at=user.created_at)
