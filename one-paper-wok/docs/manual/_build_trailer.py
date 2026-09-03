#!/usr/bin/env python3
"""Compose a cinematic 1080p product trailer for 一纸读书煲."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace/one-paper-wok/docs/manual")
IMG = ROOT / "images"
ASSETS = Path("/opt/cursor/artifacts/assets")
BUILD = Path("/tmp/trailer-build")
BUILD.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "一纸读书煲-产品预告.mp4"
ART = Path("/opt/cursor/artifacts/one_paper_wok_product_trailer.mp4")

W, H = 1920, 1080
FPS = 30
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def load(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def cover_resize(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def darken(im: Image.Image, alpha: float = 0.38) -> Image.Image:
    overlay = Image.new("RGB", im.size, (28, 18, 12))
    return Image.blend(im, overlay, alpha)


def gradient_left(im: Image.Image) -> Image.Image:
    """Keep left readable for type; right stays photographic."""
    base = im.convert("RGBA")
    g = Image.new("L", base.size, 0)
    gd = ImageDraw.Draw(g)
    for x in range(W):
        v = int(max(0, min(180, (620 - x) * 0.42)))
        gd.line([(x, 0), (x, H)], fill=v)
    shade = Image.new("RGBA", base.size, (20, 12, 8, 0))
    shade.putalpha(g)
    return Image.alpha_composite(base, shade).convert("RGB")


def round_phone(src: Path, height: int = 860, radius: int = 48) -> Image.Image:
    phone = load(src).convert("RGBA")
    scale = height / phone.height
    phone = phone.resize((int(phone.width * scale), height), Image.Resampling.LANCZOS)
    bezel = 14
    canvas = Image.new("RGBA", (phone.width + bezel * 2, phone.height + bezel * 2), (0, 0, 0, 0))
    body = Image.new("RGBA", canvas.size, (32, 24, 20, 255))
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, canvas.width - 1, canvas.height - 1], radius + 8, fill=255)
    body.putalpha(mask)
    inner_mask = Image.new("L", phone.size, 0)
    ImageDraw.Draw(inner_mask).rounded_rectangle([0, 0, phone.width - 1, phone.height - 1], radius, fill=255)
    phone.putalpha(inner_mask)
    canvas = Image.alpha_composite(canvas, body)
    canvas.paste(phone, (bezel, bezel), phone)
    shadow = Image.new("RGBA", (canvas.width + 80, canvas.height + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 140))
    sh.putalpha(mask.point(lambda p: int(p * 0.45)))
    shadow.paste(sh, (28, 36), sh)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    out = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, shadow)
    out.paste(canvas, (12, 8), canvas)
    return out


def draw_text(draw: ImageDraw.ImageDraw, xy, text, size, fill, shadow=True):
    f = font(size)
    x, y = xy
    if shadow:
        draw.text((x + 2, y + 3), text, font=f, fill=(0, 0, 0, 140))
    draw.text((x, y), text, font=f, fill=fill)


def caption(im: Image.Image, kicker: str, title: str, sub: str | None = None) -> Image.Image:
    im = im.convert("RGBA")
    draw = ImageDraw.Draw(im)
    x, y = 88, 150
    if kicker:
        draw_text(draw, (x, y), kicker, 28, (232, 115, 74, 255))
        y += 54
    draw_text(draw, (x, y), title, 72, (255, 250, 244, 255))
    if sub:
        y += 102
        # wrap-ish
        draw_text(draw, (x, y), sub, 32, (235, 222, 208, 255))
    # orange rule
    draw.rectangle([x, 128, x + 72, 134], fill=(232, 115, 74, 255))
    return im.convert("RGB")


def place_phone(bg: Image.Image, phone: Image.Image, x: int, y: int) -> Image.Image:
    canvas = bg.convert("RGBA")
    canvas.alpha_composite(phone, (x, y))
    return canvas.convert("RGB")


def scene_bleed(bg: Path, kicker, title, sub, dark=0.42) -> Image.Image:
    im = gradient_left(darken(cover_resize(load(bg), (W, H)), dark))
    return caption(im, kicker, title, sub)


def scene_phone(bg: Path, shot: Path, kicker, title, sub, dark=0.5, px=1180, py=90) -> Image.Image:
    im = gradient_left(darken(cover_resize(load(bg), (W, H)), dark))
    im = caption(im, kicker, title, sub)
    phone = round_phone(shot)
    return place_phone(im, phone, px, py)


def scene_dual(bg: Path, left: Path, right: Path, kicker, title, sub) -> Image.Image:
    im = gradient_left(darken(cover_resize(load(bg), (W, H)), 0.55))
    im = caption(im, kicker, title, sub)
    p1 = round_phone(left, height=760)
    p2 = round_phone(right, height=760)
    im = place_phone(im, p1, 980, 140)
    im = place_phone(im, p2, 1380, 200)
    return im


def make_music(path: Path, seconds: float) -> None:
    sr = 44100
    n = int(sr * seconds)
    t = np.linspace(0, seconds, n, endpoint=False)
    # Warm progression F – C – Dm – Bb, 4s each, looping
    roots = [174.61, 130.81, 146.83, 116.54]
    sig = np.zeros(n)
    for i, root in enumerate(roots * 6):
        start = int(i * 4 * sr)
        if start >= n:
            break
        end = min(n, start + int(5.2 * sr))
        tt = t[start:end] - t[start]
        env = np.minimum(1, tt / 0.8) * np.exp(-tt * 0.18)
        env = np.clip(env, 0, 1)
        chord = [root, root * 5 / 4, root * 3 / 2, root * 2]
        tone = sum(0.22 / (k + 1) * np.sin(2 * np.pi * f * tt) for k, f in enumerate(chord))
        # gentle detune
        tone += 0.06 * np.sin(2 * np.pi * root * 1.003 * tt)
        sig[start:end] += tone * env * 0.28
    # slow shimmer
    sig += 0.03 * np.sin(2 * np.pi * 659.25 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
    # fade
    fade = int(sr * 2.2)
    sig[:fade] *= np.linspace(0, 1, fade)
    sig[-fade:] *= np.linspace(1, 0, fade)
    # soft limiter
    peak = np.max(np.abs(sig)) + 1e-9
    sig = 0.85 * sig / peak
    pcm = (sig * 32767).astype(np.int16)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def zoom_clip(png: Path, mp4: Path, seconds: float, zoom_end: float = 1.12) -> None:
    frames = int(seconds * FPS)
    # scale up then zoompan
    vf = (
        f"scale=2304:1296:force_original_aspect_ratio=increase,"
        f"crop=2304:1296,"
        f"zoompan=z='min(1+{zoom_end-1}*on/{frames}, {zoom_end})':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=1920x1080:fps={FPS},"
        f"vignette=PI/5,"
        f"eq=saturation=1.05:gamma=0.98:contrast=1.04"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(png),
            "-vf", vf, "-t", f"{seconds:.2f}", "-r", str(FPS),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            str(mp4),
        ],
        check=True,
        capture_output=True,
    )


def concat_xfade(clips: list[tuple[Path, float]], fade: float, out: Path) -> None:
    args = ["ffmpeg", "-y"]
    for p, _ in clips:
        args += ["-i", str(p)]
    n = len(clips)
    filters = []
    # chain xfade
    current = "0:v"
    timeline = clips[0][1]
    for i in range(1, n):
        offset = timeline - fade
        label = f"v{i}"
        filters.append(
            f"[{current}][{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[{label}]"
        )
        current = label
        timeline = timeline + clips[i][1] - fade
    fc = ";".join(filters)
    last = current if n > 1 else "0:v"
    args += ["-filter_complex", fc, "-map", f"[{last}]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-preset", "medium", "-crf", "17", str(out)]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-4000:])


def mux(video: Path, audio: Path, out: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart", str(out),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    cover = IMG / "cover.png"
    sanctuary = ASSETS / "trailer_01_sanctuary.png"
    scan_bg = ASSETS / "trailer_02_scan.png"
    ai = ASSETS / "trailer_03_ai_wok.png"
    paper = ASSETS / "trailer_04_one_paper.png"
    recook = ASSETS / "trailer_05_recook.png"
    end = ASSETS / "trailer_06_endcard.png"

    scenes: list[tuple[str, float, Image.Image]] = [
        ("01", 4.2, scene_bleed(sanctuary, "精神庇护所", "纸书不该只被合上", "它值得再被慢炖一次")),
        ("02", 4.0, scene_bleed(cover, "产品预告", "一纸读书煲", "一个有趣的精神庇护所")),
        ("03", 4.6, scene_phone(sanctuary, IMG / "01_login.png", "01 打开", "连上你的锅", "云端就绪，一键进入")),
        ("04", 3.6, scene_phone(sanctuary, IMG / "04_library_empty.png", "02 我的锅", "从一口空锅开始", "书架，也可以是灶台")),
        ("05", 4.0, scene_bleed(scan_bg, "03 备料", "把一页纸放进锅里", "相机即砧板")),
        ("06", 4.2, scene_phone(scan_bg, IMG / "07_scan.png", "03 备料", "拍摄或从相册导入", "全书自炊  ·  轻摘录")),
        ("07", 5.2, scene_bleed(ai, "04 AI 慢炖", "OCR  章节  一纸精华", "让模型在锅里慢慢工作")),
        ("08", 4.2, scene_phone(ai, IMG / "09_cooking.png", "04 慢炖中", " ident 正在识别文字", "你可以离开，锅会继续")),
        ("09", 4.6, scene_phone(paper, IMG / "13_project.png", "05 出锅", "一纸看懂一本书", "摘要、洞察、章节提纲")),
        ("10", 5.0, scene_dual(paper, IMG / "11_reader.png", IMG / "12_reader_translate.png", "06 阅读", "可搜索，可翻译", "PDF  EPUB  对照译文")),
        ("11", 4.6, scene_phone(recook, IMG / "14_notebook.png", "07 回锅", "手写批注再入锅", "你的旁注，成为一纸的一部分")),
        ("12", 3.8, scene_phone(sanctuary, IMG / "06_library_books.png", "08 同步", "换设备，锅还在", "账号跟着你走")),
        ("13", 5.4, scene_bleed(end, "", "一纸读书煲", "把阅读，重新煮成生活")),
    ]
    # fix accidental latin in scene 08
    scenes[7] = (
        "08",
        4.2,
        scene_phone(ai, IMG / "09_cooking.png", "04 慢炖中", "正在识别文字", "你可以离开，锅会继续"),
    )

    clips: list[tuple[Path, float]] = []
    for name, dur, im in scenes:
        png = BUILD / f"{name}.png"
        im.save(png, "PNG")
        mp4 = BUILD / f"{name}.mp4"
        zoom = 1.08 if name not in {"02", "13"} else 1.05
        zoom_clip(png, mp4, dur, zoom)
        clips.append((mp4, dur))
        print("clip", name, dur)

    faded = BUILD / "picture.mp4"
    concat_xfade(clips, fade=0.7, out=faded)
    total = sum(d for _, d in clips) - 0.7 * (len(clips) - 1)
    print("picture seconds", total)
    wav = BUILD / "score.wav"
    make_music(wav, total + 1.5)
    mux(faded, wav, OUT)
    subprocess.run(["cp", str(OUT), str(ART)], check=True)
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
