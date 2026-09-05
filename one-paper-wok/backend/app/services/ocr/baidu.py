import base64
import time

import httpx

from ...config import Settings
from .base import OcrLine, OcrProvider, OcrResult

_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
_ACCURATE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
_HANDWRITING_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting"


class BaiduOcrProvider(OcrProvider):
    """Baidu OCR: 通用文字识别（高精度含位置） for printed pages, 手写文字识别 for annotations."""

    name = "baidu"

    def __init__(self, settings: Settings) -> None:
        if not settings.baidu_ocr_api_key or not settings.baidu_ocr_secret_key:
            raise ValueError("BAIDU_OCR_API_KEY / BAIDU_OCR_SECRET_KEY are required")
        self._api_key = settings.baidu_ocr_api_key
        self._secret_key = settings.baidu_ocr_secret_key
        self._token: str | None = None
        self._token_expires_at = 0.0
        self._client = httpx.Client(timeout=60)

    def _access_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        resp = self._client.post(
            _TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": self._api_key,
                "client_secret": self._secret_key,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + float(data.get("expires_in", 2592000))
        return self._token

    def recognize(self, image_bytes: bytes, *, handwriting: bool = False) -> OcrResult:
        url = _HANDWRITING_URL if handwriting else _ACCURATE_URL
        payload = {
            "image": base64.b64encode(image_bytes).decode("ascii"),
            "detect_direction": "true",
            "paragraph": "true",
        }
        if handwriting:
            payload["recognize_granularity"] = "big"
        resp = self._client.post(
            url,
            params={"access_token": self._access_token()},
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data = resp.json()
        if "error_code" in data:
            raise RuntimeError(f"Baidu OCR error {data['error_code']}: {data.get('error_msg')}")
        lines: list[OcrLine] = []
        for item in data.get("words_result", []):
            loc = item.get("location") or {}
            lines.append(
                OcrLine(
                    text=item.get("words", ""),
                    bbox=(
                        int(loc.get("left", 0)),
                        int(loc.get("top", 0)),
                        int(loc.get("width", 0)),
                        int(loc.get("height", 0)),
                    ),
                )
            )
        return OcrResult(text="\n".join(line.text for line in lines), lines=lines)
