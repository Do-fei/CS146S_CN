import io
from pathlib import Path

from PIL import Image, ImageOps

from ..config import get_settings
from ..models import new_id


def ensure_dirs() -> None:
    s = get_settings()
    s.uploads_dir.mkdir(parents=True, exist_ok=True)
    s.outputs_dir.mkdir(parents=True, exist_ok=True)


def preprocess_image(raw: bytes) -> bytes:
    """Apply EXIF orientation, convert to RGB, downscale to max_image_side and re-encode as JPEG."""
    s = get_settings()
    with Image.open(io.BytesIO(raw)) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        w, h = img.size
        longest = max(w, h)
        if longest > s.max_image_side:
            scale = s.max_image_side / longest
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=88, optimize=True)
        return out.getvalue()


def save_upload(book_id: str, subdir: str, raw: bytes) -> Path:
    ensure_dirs()
    target_dir = get_settings().uploads_dir / book_id / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{new_id()}.jpg"
    path.write_bytes(preprocess_image(raw))
    return path


def output_path(book_id: str, filename: str) -> Path:
    ensure_dirs()
    target_dir = get_settings().outputs_dir / book_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size
