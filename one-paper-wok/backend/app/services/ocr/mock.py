import hashlib

from .base import OcrLine, OcrProvider, OcrResult

_PRINTED_SAMPLES = [
    "人类思维有两套系统。系统1快速、直觉、自动运行；系统2缓慢、理性、需要努力。",
    "我们大多数时候以为自己在用系统2思考，实际上系统1才是决策的主宰。",
    "眼见即为事实：我们高估已经看到的信息，忽略尚未看到的部分。",
    "框架效应说明，同一事实的不同表述方式会显著改变人们的选择。",
    "体验自我与记忆自我并不一致，我们对过去的评价并不等于当时的真实体验。",
    "锚定效应：最先出现的数字会成为后续判断的参照点，即使它毫无关联。",
]

_HANDWRITING_SAMPLES = [
    "这个框架可以直接用在产品设计上——用户看到的第一个价格就是锚点。",
    "想到自己做决策时也常常被系统1牵着走，需要刻意放慢。",
    "把这一章的结论和团队的复盘流程结合起来。",
]


class MockOcrProvider(OcrProvider):
    """Deterministic stand-in for cloud OCR so the whole pipeline runs without credentials."""

    name = "mock"

    def recognize(self, image_bytes: bytes, *, handwriting: bool = False) -> OcrResult:
        digest = hashlib.sha1(image_bytes).digest()
        samples = _HANDWRITING_SAMPLES if handwriting else _PRINTED_SAMPLES
        start = digest[0] % len(samples)
        count = 1 if handwriting else 3
        chosen = [samples[(start + i) % len(samples)] for i in range(count)]
        lines = [OcrLine(text=t, bbox=(40, 60 + i * 48, 900, 40)) for i, t in enumerate(chosen)]
        return OcrResult(text="\n".join(chosen), lines=lines)
