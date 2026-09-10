from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class OcrLine:
    text: str
    # left, top, width, height in pixels of the source image (may be zeros when unknown)
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)


@dataclass
class OcrResult:
    text: str
    lines: list[OcrLine] = field(default_factory=list)


class OcrProvider(ABC):
    name: str = "base"

    @abstractmethod
    def recognize(self, image_bytes: bytes, *, handwriting: bool = False) -> OcrResult: ...
