#!/usr/bin/env python3
"""Slice the approved ink-wok master into Android launcher densities."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MASTER = Path(__file__).resolve().parents[1] / "branding" / "icon-iron-wok-master.png"
RES = ROOT / "app/src/main/res"
PAPER = (243, 239, 230, 255)
LEGACY = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
ADAPTIVE_FG = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}


def contain(im: Image.Image, size: int, pad_ratio: float = 0.18) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inner = int(size * (1 - 2 * pad_ratio))
    fitted = im.resize((inner, inner), Image.Resampling.LANCZOS)
    xy = (size - inner) // 2
    canvas.paste(fitted, (xy, xy), fitted)
    return canvas


def circle_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((1, 1, size - 2, size - 2), fill=255)
    return mask


def main() -> None:
    src = Image.open(MASTER).convert("RGBA")
    # Master already has paper; keep full art for legacy, inset for adaptive crop.
    for density, px in LEGACY.items():
        folder = RES / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        legacy = Image.new("RGBA", (px, px), PAPER)
        art = src.resize((px, px), Image.Resampling.LANCZOS)
        legacy.paste(art, (0, 0), art)
        legacy.save(folder / "ic_launcher.png", optimize=True)
        rounded = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        rounded.paste(legacy, (0, 0))
        rounded.putalpha(circle_mask(px))
        bg = Image.new("RGBA", (px, px), PAPER)
        bg.paste(rounded, (0, 0), rounded)
        bg.save(folder / "ic_launcher_round.png", optimize=True)

        fg = contain(src, ADAPTIVE_FG[density], pad_ratio=0.16)
        fg.save(folder / "ic_launcher_foreground.png", optimize=True)

    preview = Image.new("RGBA", (512, 512), PAPER)
    preview.paste(src.resize((512, 512), Image.Resampling.LANCZOS), (0, 0))
    out = Path("/opt/cursor/artifacts/app_icon_iron_wok_final.png")
    preview.save(out, optimize=True)
    print("wrote mipmaps and", out)


if __name__ == "__main__":
    main()
