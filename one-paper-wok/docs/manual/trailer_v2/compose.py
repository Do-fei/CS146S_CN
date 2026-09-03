#!/usr/bin/env python3
"""Apple-style product trailer: sparse VO, licensed score, motion graphics."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parent
MANUAL = ROOT.parent
PLATES = ROOT / "plates"
UI = ROOT / "ui"
BUILD = Path("/tmp/trailer2-build")
BUILD.mkdir(parents=True, exist_ok=True)
FRAMES = BUILD / "frames"
FRAMES.mkdir(parents=True, exist_ok=True)
FONT = Path("/tmp/trailer2/NotoSansSC.ttf")
OUT = MANUAL / "一纸读书煲-产品预告.mp4"
ART = Path("/opt/cursor/artifacts/one_paper_wok_apple_trailer.mp4")

W, H, FPS = 1920, 1080, 30
ORANGE = (232, 115, 74)
CREAM = (246, 243, 238)


def font(size: int, weight: float = 300) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def load_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    s = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * s + 1), int(im.height * s + 1)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    l = (nw - tw) // 2
    t = (nh - th) // 2
    return im.crop((l, t, l + tw, t + th))


def ken(im: Image.Image, t: float, zoom0: float = 1.0, zoom1: float = 1.08, panx: float = 0.0) -> Image.Image:
    z = lerp(zoom0, zoom1, ease_in_out(t))
    cw, ch = int(W * z), int(H * z)
    big = cover(im, (cw, ch))
    x = int((big.width - W) * (0.5 + panx * (t - 0.5)))
    y = int((big.height - H) * 0.42)
    x = max(0, min(big.width - W, x))
    y = max(0, min(big.height - H, y))
    return big.crop((x, y, x + W, y + H))


def device_frame(src: Path, height: int = 860) -> Image.Image:
    ui = Image.open(src).convert("RGBA")
    scale = height / ui.height
    ui = ui.resize((max(1, int(ui.width * scale)), height), Image.Resampling.LANCZOS)
    r, bezel = 54, 11
    w, h = ui.size
    cw, ch = w + bezel * 2, h + bezel * 2
    body = Image.new("RGBA", (cw, ch), (10, 10, 12, 255))
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], r + 6, fill=255)
    body.putalpha(mask)
    inner = Image.new("L", ui.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    ui.putalpha(inner)
    body.paste(ui, (bezel, bezel), ui)
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([cw / 2 - 58, 16, cw / 2 + 58, 48], 16, fill=(0, 0, 0, 255))
    # specular edge
    spec = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spec)
    sd.rounded_rectangle([1, 1, cw - 2, ch - 2], r + 5, outline=(255, 255, 255, 48), width=2)
    body = Image.alpha_composite(body, spec)
    # drop shadow
    pad = 70
    canvas = Image.new("RGBA", (cw + pad, ch + pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 180))
    sh.putalpha(mask.point(lambda p: int(p * 0.55)))
    canvas.paste(sh, (28, 36), sh)
    canvas = canvas.filter(ImageFilter.GaussianBlur(24))
    canvas.alpha_composite(body, (12, 8))
    return canvas


def reflection(phone: Image.Image, fade: float = 0.28) -> Image.Image:
    r = phone.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    r = r.crop((0, 0, r.width, int(r.height * 0.38)))
    r = r.filter(ImageFilter.GaussianBlur(6))
    a = r.split()[-1].point(lambda p: int(p * fade))
    r.putalpha(a)
    return r


def paste(bg: Image.Image, layer: Image.Image, xy: tuple[int, int], opacity: float = 1.0) -> Image.Image:
    if opacity <= 0:
        return bg
    if opacity < 0.999:
        layer = layer.copy()
        a = layer.split()[-1].point(lambda p: int(p * opacity))
        layer.putalpha(a)
    canvas = bg.convert("RGBA")
    canvas.alpha_composite(layer, xy)
    return canvas


def text_block(lines: list[tuple[str, int, float]], color=CREAM) -> Image.Image:
    """Pre-render left-aligned type. lines: (text, size, weight)."""
    im = Image.new("RGBA", (980, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 8
    d.rectangle([0, 0, 44, 3], fill=ORANGE + (255,))
    y = 28
    for text, size, weight in lines:
        f = font(size, weight)
        d.text((0, y), text, font=f, fill=color + (255,))
        y += int(size * 1.28)
    return im


def vignette() -> Image.Image:
    arr = np.zeros((H, W), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W / 2, H / 2
    r = np.sqrt(((xx - cx) / (W * 0.72)) ** 2 + ((cy - yy) / (H * 0.78)) ** 2)
    arr = np.clip(1.15 - r * 0.55, 0.42, 1.0)
    rgb = np.stack([arr, arr, arr], axis=2)
    return Image.fromarray((rgb * 255).astype(np.uint8), "RGB")


def grains() -> list[Image.Image]:
    out = []
    rng = np.random.default_rng(7)
    for i in range(6):
        n = rng.integers(0, 40, (H, W, 1), dtype=np.uint8)
        a = Image.fromarray(np.repeat(n, 3, axis=2), "RGB")
        out.append(a)
    return out


def sweep_strip() -> Image.Image:
    sw = 220
    im = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    px = im.load()
    for x in range(sw):
        a = int(70 * math.exp(-0.5 * ((x - sw / 2) / 36) ** 2))
        for y in range(H):
            px[x, y] = (255, 236, 220, a)
    return im


def scan_strip() -> Image.Image:
    sh = 90
    im = Image.new("RGBA", (W, sh), (0, 0, 0, 0))
    px = im.load()
    for y in range(sh):
        a = int(210 * math.exp(-0.5 * ((y - sh / 2) / 12) ** 2))
        for x in range(W):
            px[x, y] = (232, 115, 74, a)
    return im.filter(ImageFilter.GaussianBlur(4))


def apply_vignette(im: Image.Image, vig: Image.Image) -> Image.Image:
    return ImageEnhance.Brightness(im).enhance(1.0)  # placeholder, use multiply
    # actually:
    # return ImageChops.multiply — need import


from PIL import ImageChops  # noqa: E402


def grade(im: Image.Image, vig: Image.Image, grain: Image.Image, t: float) -> Image.Image:
    im = ImageChops.multiply(im, vig)
    g = Image.blend(im, grain, 0.045)
    # slight contrast
    g = ImageEnhance.Contrast(g).enhance(1.06)
    g = ImageEnhance.Color(g).enhance(1.05)
    return g


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-4000:] if r.stderr else r.stdout[-2000:])


def make_vo(cues: list[tuple[float, str]], total: float, path: Path) -> None:
    import asyncio
    import edge_tts

    clips = []

    async def synth() -> None:
        for i, (_, text) in enumerate(cues):
            out = BUILD / f"vo_{i:02d}.mp3"
            comm = edge_tts.Communicate(
                text,
                voice="zh-CN-YunxiNeural",
                rate="-14%",
                pitch="-3Hz",
            )
            await comm.save(str(out))
            clips.append(out)

    asyncio.run(synth())
    # pad into a single stereo 44100 wav
    parts = []
    sr = 44100
    cursor = 0.0
    silence_needed = []
    for i, (start, _) in enumerate(cues):
        gap = start - cursor
        if gap > 0.02:
            parts.append(("silence", gap))
        parts.append(("file", clips[i]))
        # probe duration
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clips[i])],
            capture_output=True, text=True, check=True,
        )
        dur = float(p.stdout.strip())
        cursor = start + dur
    if cursor < total:
        parts.append(("silence", total - cursor + 0.4))

    concat = BUILD / "vo_concat.txt"
    wavs = []
    lines = []
    for j, item in enumerate(parts):
        if item[0] == "silence":
            s = BUILD / f"sil_{j}.wav"
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", f"{item[1]:.3f}", str(s)])
            wavs.append(s)
        else:
            w = BUILD / f"vo_{j}.wav"
            run(["ffmpeg", "-y", "-i", str(item[1]), "-ar", str(sr), "-ac", "1", str(w)])
            wavs.append(w)
        lines.append(f"file '{wavs[-1]}'")
    concat.write_text("\n".join(lines))
    raw = BUILD / "vo_raw.wav"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(raw)])
    # gentle plate reverb-ish + presence
    run([
        "ffmpeg", "-y", "-i", str(raw),
        "-af", "highpass=f=80,lowpass=f=10500,aecho=0.82:0.7:28:0.08,loudnorm=I=-16:TP=-1.5:LRA=11",
        str(path),
    ])


def make_music(total: float, path: Path) -> None:
    crypto = Path("/tmp/score/crypto.mp3")
    awash = Path("/tmp/score/light_awash.mp3")
    # Light Awash = airy bed; Crypto = tech pulse, ducked
    run([
        "ffmpeg", "-y",
        "-ss", "8", "-i", str(awash),
        "-ss", "12", "-i", str(crypto),
        "-filter_complex",
        f"[0:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,volume=0.20,afade=t=in:d=2.4,afade=t=out:st={total-4:.2f}:d=4[a];"
        f"[1:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,highpass=f=180,volume=0.13,afade=t=in:d=3,afade=t=out:st={total-4:.2f}:d=4[b];"
        f"[a][b]amix=inputs=2:duration=first:dropout_transition=2[m]",
        "-map", "[m]", "-ar", "44100", str(path),
    ])


def mix_audio(vo: Path, music: Path, total: float, path: Path) -> None:
    # duck music a little under VO
    run([
        "ffmpeg", "-y", "-i", str(music), "-i", str(vo),
        "-filter_complex",
        "[1:a]asplit=2[vox][side];"
        "[side]volume=4,lowpass=f=250[env];"
        "[0:a][env]sidechaincompress=threshold=0.05:ratio=5:attack=40:release=420:makeup=1[ducked];"
        "[ducked][vox]amix=inputs=2:duration=first:weights=0.9 1.15,alimiter=limit=0.95[a]",
        "-map", "[a]", "-t", f"{total:.2f}", "-c:a", "aac", "-b:a", "192k", str(path),
    ])


def main() -> None:
    shots = [
        ("open", 6.4),
        ("home", 6.8),
        ("scan", 7.0),
        ("cook", 6.8),
        ("paper", 6.6),
        ("read", 7.2),
        ("note", 6.6),
        ("end", 7.2),
    ]
    starts = []
    acc = 0.0
    for name, dur in shots:
        starts.append(acc)
        acc += dur
    total = acc
    fade = 0.55
    print("duration", total)
    vo_path = BUILD / "vo.wav"
    music_path = BUILD / "music.wav"
    aac = BUILD / "mix.m4a"
    cues = [
        (1.55, "书，不该只被合上。"),
        (8.35, "把它，放进锅里。"),
        (16.2, "文字，会醒来。"),
        (24.8, "一页，看懂一整本。"),
        (35.4, "对照，再问一句。"),
        (43.2, "一纸读书煲。"),
        (47.6, "把阅读，重新煮成生活。"),
    ]
    print("synth vo")
    if not vo_path.exists():
        make_vo(cues, total, vo_path)
    print("mix music")
    if not aac.exists():
        make_music(total, music_path)
        mix_audio(vo_path, music_path, total, aac)

    plates = {p.stem: cover(load_rgb(p), (W, H)) for p in PLATES.glob("plate_*.png")}
    phones = {
        name: device_frame(UI / f"{name}.png", 700 if name != "scan" else 720)
        for name in ("home", "scan", "cook", "paper", "reader", "companion", "canteen", "note")
    }
    phones_s = {k: device_frame(UI / f"{k}.png", 600) for k in ("reader", "companion", "canteen", "home")}
    refs = {k: reflection(v) for k, v in phones.items()}
    vig = vignette()
    grain_loop = grains()
    sweep = sweep_strip()
    laser = scan_strip()

    titles = {
        "open": text_block([("书，不该只被合上。", 64, 280)]),
        "home": text_block([("把它，放进锅里。", 64, 280), ("从一口空锅开始。", 28, 350)]),
        "scan": text_block([("文字，会醒来。", 64, 280), ("对准纸面。即刻入锅。", 28, 350)]),
        "cook": text_block([("AI 在慢炖。", 64, 280), ("OCR  ·  章节  ·  一纸精华", 26, 350)]),
        "paper": text_block([("一页，看懂一整本。", 64, 280)]),
        "read": text_block([("对照。搜索。再问一句。", 56, 280)]),
        "note": text_block([("你的批注，继续炖。", 60, 280)]),
        "end": text_block([("一纸读书煲", 78, 250), ("把阅读，重新煮成生活。", 32, 330)]),
    }

    # particle seeds
    rng = np.random.default_rng(3)
    n_p = 90
    px0 = rng.uniform(620, 1280, n_p)
    py0 = rng.uniform(420, 760, n_p)
    pvx = rng.uniform(30, 220, n_p)
    pvy = rng.uniform(-240, -40, n_p)
    psz = rng.uniform(1.4, 4.2, n_p)

    def shot_local(t: float) -> tuple[str, float, float]:
        for i, (name, dur) in enumerate(shots):
            s = starts[i]
            if t < s + dur or i == len(shots) - 1:
                return name, max(0.0, t - s), dur
        return shots[-1][0], 0.0, shots[-1][1]

    def draw_particles(base: Image.Image, t: float) -> Image.Image:
        im = base.convert("RGBA")
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(n_p):
            x = px0[i] + pvx[i] * t
            y = py0[i] + pvy[i] * t
            life = max(0.0, 1.0 - t * 0.35 - (i % 7) * 0.03)
            if life <= 0 or x < 0 or y < 0 or x > W or y > H:
                continue
            a = int(200 * life)
            r = psz[i]
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 176, 110, a))
        return im.convert("RGB")

    def compose_shot(name: str, lt: float, dur: float) -> Image.Image:
        u = lt / max(dur, 0.001)
        title_op = ease_in_out(min(1, lt / 0.7)) * (1 if u < 0.82 else ease_in_out((1 - u) / 0.18))
        phone_in = ease_out(min(1, lt / 0.95))

        if name == "open":
            bg = ken(plates["plate_book_void"], u, 1.02, 1.10)
            # radial bloom
            bloom = Image.new("RGB", (W, H), (0, 0, 0))
            bd = ImageDraw.Draw(bloom)
            rad = int(lerp(40, 520, ease_out(min(1, lt / 2.2))))
            bd.ellipse([W / 2 - rad, H / 2 - rad * 0.55, W / 2 + rad, H / 2 + rad * 0.55], fill=(40, 22, 14))
            bloom = bloom.filter(ImageFilter.GaussianBlur(80))
            bg = ImageChops.add(bg, ImageEnhance.Brightness(bloom).enhance(0.55))
            bg = paste(bg, titles["open"], (100, 430), title_op)

        elif name == "home":
            bg = ken(plates["plate_table_still"], u, 1.0, 1.07, panx=0.08)
            ph = phones["home"]
            x = int(lerp(W + 40, 1220, phone_in))
            y = 128
            bg = paste(bg, ph, (x, y), 0.15 + 0.85 * phone_in)
            rf = refs["home"]
            bg = paste(bg, rf, (x, y + ph.height - 28), 0.7 * phone_in)
            bg = paste(bg, titles["home"], (96, 360), title_op)

        elif name == "scan":
            bg = ken(plates["plate_pages_light"], u, 1.0, 1.09)
            bg = draw_particles(bg, lt)
            ly = int(lerp(180, 860, ease_in_out((lt % 2.4) / 2.4)))
            bg = paste(bg, laser, (0, ly - 45), 0.85)
            ph = phones["scan"]
            x, y = 1235, int(lerp(160, 100, phone_in))
            bg = paste(bg, ph, (x, y), phone_in)
            bg = paste(bg, titles["scan"], (88, 340), title_op)

        elif name == "cook":
            bg = ken(plates["plate_wok_steam"], u, 1.0, 1.08)
            # orbiting glyphs
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            glyphs = list("OCR章节精华文字醒来慢炖")
            f = font(22, 350)
            for i, ch in enumerate(glyphs):
                ang = lt * 0.85 + i * (math.tau / len(glyphs))
                cx, cy = 640, 540
                rx, ry = 230, 118
                x = cx + rx * math.cos(ang)
                y = cy + ry * math.sin(ang)
                od.text((x, y), ch, font=f, fill=(255, 210, 170, 170))
            bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
            ph = phones["cook"]
            bg = paste(bg, ph, (1230, 120), phone_in)
            bg = paste(bg, titles["cook"], (88, 330), title_op)

        elif name == "paper":
            bg = ken(plates["plate_glyphs"], u, 1.02, 1.09)
            ph = phones["paper"]
            bg = paste(bg, ph, (int(lerp(1280, 1230, phone_in)), 118), phone_in)
            bg = paste(bg, titles["paper"], (88, 400), title_op)

        elif name == "read":
            bg = ken(plates["plate_phone_glass"], u, 1.0, 1.06)
            bg = ImageEnhance.Brightness(bg).enhance(0.55)
            p1 = phones_s["reader"]
            p2 = phones_s["companion"]
            x1 = int(lerp(420, 1020, phone_in))
            x2 = int(lerp(1620, 1395, phone_in))
            bg = paste(bg, p1, (x1, 200), phone_in)
            bg = paste(bg, p2, (x2, 248), phone_in)
            bg = paste(bg, titles["read"], (88, 320), title_op)

        elif name == "note":
            bg = ken(plates["plate_devices"], u, 1.0, 1.07)
            p1 = phones_s["note"] if "note" in phones_s else phones["note"]
            p1 = phones["note"]
            p2 = phones_s["canteen"]
            bg = paste(bg, p1, (int(lerp(220, 1100, phone_in)), 120), phone_in)
            bg = paste(bg, p2, (int(lerp(1720, 1455, phone_in)), 240), phone_in * 0.95)
            bg = paste(bg, titles["note"], (88, 360), title_op)

        else:  # end
            bg = ken(plates["plate_book_void"], u, 1.06, 1.12)
            bg = ImageEnhance.Brightness(bg).enhance(lerp(0.7, 0.35, u))
            word = titles["end"]
            bg = paste(bg, word, (100, 390), title_op)
            credit = text_block([("Music  Crypto & Light Awash  ·  Kevin MacLeod  ·  CC BY", 16, 350)])
            bg = paste(bg, credit, (100, 980), min(1.0, max(0, (lt - 2.2) / 0.8)) * 0.7)

        # light sweep
        sx = int(lerp(-240, W + 40, (lt / 3.6) % 1.0))
        bg = paste(bg, sweep, (sx, 0), 0.55)
        return bg.convert("RGB")

    nframes = int(total * FPS)
    print("frames", nframes)
    prev_name = None
    # crossfade buffer: keep last frames of previous shot? easier: blend with black at edges
    for i in range(nframes):
        t = i / FPS
        name, lt, dur = shot_local(t)
        frame = compose_shot(name, lt, dur)
        # fade through black at shot edges
        edge = min(lt, dur - lt)
        if edge < fade and not (name == "open" and lt < fade):
            k = ease_in_out(edge / fade)
            black = Image.new("RGB", (W, H), (0, 0, 0))
            frame = Image.blend(black, frame, k)
        if name == "open" and lt < 1.1:
            frame = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), frame, ease_in_out(lt / 1.1))
        if name == "end" and dur - lt < 1.4:
            frame = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), frame, ease_in_out((dur - lt) / 1.4))
        frame = grade(frame, vig, grain_loop[i % len(grain_loop)], t)
        frame.save(FRAMES / f"{i:05d}.jpg", quality=90, optimize=False, subsampling=1)
        if i % 60 == 0:
            print("frame", i, f"{t:.1f}s", name)

    pic = BUILD / "picture.mp4"
    run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "%05d.jpg"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "17",
        "-movflags", "+faststart", str(pic),
    ])
    run([
        "ffmpeg", "-y", "-i", str(pic), "-i", str(aac),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", str(OUT),
    ])
    subprocess.run(["cp", str(OUT), str(ART)], check=True)
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
