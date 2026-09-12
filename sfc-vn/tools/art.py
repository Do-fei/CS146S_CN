"""绘画场景与立绘：网页用高清音小说插画，卡带仍用量化和几何底图。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
ART_ROOT = Path(__file__).resolve().parents[1] / "art"
SCENE_DIR = ART_ROOT / "scenes"
PORTRAIT_DIR = ART_ROOT / "portraits"
W, H = 256, 224
WEB_SCENE = (768, 672)
WEB_PORTRAIT = (360, 480)
SNES_PORTRAIT = (72, 96)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def new_scene(bg: tuple[int, int, int]) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, H), bg)
    return im, ImageDraw.Draw(im)


def _cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return im.crop((left, top, left + tw, top + th))


def _open_rgb(path: Path) -> Image.Image | None:
    if path.exists():
        return Image.open(path).convert("RGB")
    return None


def _fallback_scene(name: str) -> Image.Image:
    aliases = {
        "hutong": "street_rain",
        "avenue": "street_rain",
        "xidan_road": "street_rain",
        "aqua_road": "street_rain",
        "home_rain": "street_rain",
        "nameless_lane": "street_rain",
        "morning_st": "street_rain",
        "dawn_apt": "apartment",
        "mall_mid": "mall",
        "aqua_tunnel": "tank",
        "riverbank": "overpass",
        "metro_gate": "subway",
        "gap_tunnel": "subway",
        "pale_dawn": "rooftop",
        "duty_room": "aquarium",
        "wave_plat": "platform",
    }
    key = aliases.get(name, name)
    fn = {
        "title": _title,
        "apartment": _apartment,
        "elevator": _elevator,
        "street_rain": _street_rain,
        "store": _store,
        "overpass": _overpass,
        "mall": _mall,
        "tape_shop": _tape_shop,
        "tape_back": _tape_back,
        "aquarium": _aquarium,
        "tank": _tank,
        "pump": _pump,
        "bus": _bus,
        "subway": _subway,
        "platform": _platform,
        "rooftop": _rooftop,
    }.get(key, _street_rain)
    return fn()


def paint_scene(name: str, size: tuple[int, int] = (W, H), *, painted: bool = True) -> Image.Image:
    src = None
    if painted:
        src = _open_rgb(SCENE_DIR / f"{name}.jpg") or _open_rgb(SCENE_DIR / f"{name}.png")
    if src is None:
        src = _fallback_scene(name)
    if src.size != size:
        return _cover(src, size)
    return src


def paint_scene_web(name: str) -> Image.Image:
    return paint_scene(name, WEB_SCENE)


def _title() -> Image.Image:
    im, d = new_scene((12, 8, 36))
    for i, col in enumerate(((255, 60, 140), (40, 220, 255), (255, 200, 60), (90, 255, 160))):
        x = 20 + i * 58
        d.rectangle((x, 30, x + 36, 110), fill=col)
        d.rectangle((x + 6, 110, x + 30, 150), fill=(30, 24, 48))
    d.rectangle((0, 150, 255, 200), fill=(18, 28, 70))
    for x in range(0, 256, 8):
        d.line((x, 150, x + 4, 200), fill=(80, 40, 160))
    d.ellipse((188, 16, 228, 56), fill=(255, 230, 140))
    return im


def _apartment() -> Image.Image:
    im, d = new_scene((42, 28, 48))
    d.rectangle((0, 0, 255, 70), fill=(20, 16, 40))
    d.rectangle((16, 18, 100, 70), fill=(30, 50, 110))
    d.rectangle((20, 22, 96, 66), fill=(80, 140, 220))
    d.rectangle((140, 40, 172, 90), fill=(255, 170, 70))
    d.ellipse((148, 28, 164, 44), fill=(255, 210, 120))
    d.rectangle((0, 150, 255, 223), fill=(70, 44, 40))
    d.rectangle((180, 100, 230, 160), fill=(90, 50, 46))
    d.rectangle((40, 120, 110, 150), fill=(255, 90, 70))
    return im


def _elevator() -> Image.Image:
    im, d = new_scene((24, 26, 32))
    d.rectangle((48, 10, 208, 200), fill=(60, 64, 72))
    d.rectangle((58, 20, 198, 150), fill=(160, 190, 210))
    d.rectangle((58, 20, 128, 150), fill=(120, 150, 170))
    d.rectangle((210, 40, 236, 140), fill=(30, 32, 38))
    for y, col in ((50, (255, 80, 80)), (70, (80, 255, 120)), (90, (40, 40, 40)), (110, (255, 220, 80))):
        d.rectangle((216, y, 230, y + 12), fill=col)
    d.rectangle((0, 200, 255, 223), fill=(20, 20, 24))
    return im


def _street_rain() -> Image.Image:
    im, d = new_scene((16, 18, 48))
    d.rectangle((0, 130, 255, 223), fill=(28, 24, 50))
    for i, col in enumerate(((255, 40, 120), (40, 255, 210), (255, 200, 40))):
        x = 18 + i * 80
        d.rectangle((x, 36, x + 50, 130), fill=(36, 28, 70))
        d.rectangle((x + 8, 50, x + 42, 90), fill=col)
    d.ellipse((200, 12, 230, 42), fill=(255, 220, 150))
    for x in range(10, 250, 14):
        d.line((x, 0, x - 8, 140), fill=(90, 120, 200))
    d.rectangle((0, 168, 255, 190), fill=(255, 60, 140))
    return im


def _store() -> Image.Image:
    im, d = new_scene((20, 40, 36))
    d.rectangle((0, 0, 255, 40), fill=(40, 220, 90))
    d.rectangle((0, 40, 255, 50), fill=(255, 230, 80))
    d.rectangle((10, 60, 90, 150), fill=(180, 255, 220))
    d.rectangle((100, 70, 200, 160), fill=(255, 250, 230))
    d.rectangle((210, 20, 250, 80), fill=(20, 20, 24))
    d.text((214, 36), "22:59", font=_font(10), fill=(255, 80, 80))
    d.rectangle((0, 180, 255, 223), fill=(50, 70, 60))
    d.ellipse((220, 90, 246, 130), fill=(255, 120, 40))
    return im


def _overpass() -> Image.Image:
    im, d = new_scene((28, 16, 60))
    d.ellipse((20, 16, 70, 66), fill=(255, 120, 200))
    d.rectangle((0, 120, 255, 150), fill=(255, 140, 40))
    d.polygon([(0, 150), (255, 130), (255, 168), (0, 188)], fill=(90, 70, 80))
    d.rectangle((0, 168, 255, 210), fill=(20, 50, 110))
    for x in range(16, 240, 32):
        d.line((x, 122, x, 168), fill=(255, 210, 120), width=3)
    d.rectangle((0, 210, 255, 223), fill=(12, 20, 40))
    return im


def _mall() -> Image.Image:
    im, d = new_scene((18, 16, 24))
    d.rectangle((80, 10, 176, 200), fill=(50, 44, 60))
    for y in range(20, 180, 28):
        d.rectangle((90, y, 166, y + 16), fill=(255, 90, 160) if y % 56 == 20 else (80, 220, 255))
    d.rectangle((40, 40, 70, 200), fill=(30, 30, 36))
    d.rectangle((186, 40, 216, 200), fill=(30, 30, 36))
    d.rectangle((0, 200, 255, 223), fill=(10, 10, 14))
    return im


def _tape_shop() -> Image.Image:
    im, d = new_scene((70, 36, 24))
    d.rectangle((0, 0, 255, 50), fill=(120, 60, 30))
    for x in range(12, 240, 28):
        d.rectangle((x, 58, x + 20, 150), fill=(180, 100, 40))
        d.rectangle((x + 3, 64, x + 17, 86), fill=(255, 210, 80))
        d.rectangle((x + 3, 92, x + 17, 114), fill=(80, 220, 200))
    d.rectangle((200, 70, 246, 130), fill=(40, 20, 16))
    d.ellipse((210, 86, 236, 112), fill=(40, 255, 180))
    d.rectangle((0, 170, 255, 223), fill=(90, 48, 28))
    return im


def _tape_back() -> Image.Image:
    im, d = new_scene((40, 28, 36))
    d.rectangle((20, 40, 100, 160), fill=(160, 90, 70))
    d.rectangle((110, 60, 190, 170), fill=(120, 70, 90))
    d.rectangle((200, 30, 248, 110), fill=(255, 180, 140))
    for y in range(40, 100, 18):
        d.rectangle((206, y, 242, y + 14), fill=(80, 40, 50))
    d.rectangle((0, 180, 255, 223), fill=(24, 16, 20))
    return im


def _aquarium() -> Image.Image:
    im, d = new_scene((8, 24, 48))
    d.rectangle((0, 0, 255, 140), fill=(10, 60, 90))
    d.ellipse((20, 20, 120, 130), fill=(20, 180, 200))
    d.ellipse((140, 10, 250, 120), fill=(180, 40, 160))
    d.ellipse((60, 50, 90, 80), fill=(255, 255, 120))
    d.ellipse((180, 40, 210, 70), fill=(120, 255, 220))
    d.rectangle((0, 140, 255, 223), fill=(16, 32, 64))
    d.rectangle((0, 140, 255, 148), fill=(40, 255, 200))
    return im


def _tank() -> Image.Image:
    im, d = new_scene((6, 40, 70))
    d.rectangle((16, 16, 240, 168), fill=(0, 90, 130))
    for x in range(30, 220, 40):
        d.rectangle((x, 40, x + 24, 120), fill=(255, 70, 140))
        d.rectangle((x + 4, 48, x + 20, 70), fill=(255, 230, 120))
    d.ellipse((100, 90, 150, 150), fill=(80, 255, 200))
    d.rectangle((0, 168, 255, 223), fill=(0, 20, 40))
    return im


def _pump() -> Image.Image:
    im, d = new_scene((30, 24, 28))
    d.rectangle((40, 20, 216, 160), fill=(70, 60, 58))
    d.ellipse((70, 50, 120, 140), fill=(40, 140, 255))
    d.ellipse((140, 50, 190, 140), fill=(255, 60, 70))
    d.rectangle((100, 150, 150, 190), fill=(240, 240, 230))
    d.rectangle((0, 190, 255, 223), fill=(20, 16, 16))
    return im


def _bus() -> Image.Image:
    im, d = new_scene((28, 18, 20))
    d.rectangle((10, 30, 246, 150), fill=(90, 30, 30))
    d.rectangle((20, 40, 110, 100), fill=(20, 30, 50))
    d.rectangle((120, 40, 236, 100), fill=(255, 140, 40))
    d.rectangle((30, 110, 80, 140), fill=(20, 20, 24))
    d.text((34, 118), "22:59", font=_font(10), fill=(255, 60, 60))
    d.rectangle((0, 160, 255, 223), fill=(40, 20, 20))
    return im


def _subway() -> Image.Image:
    im, d = new_scene((16, 16, 22))
    d.rectangle((0, 40, 255, 160), fill=(36, 36, 48))
    d.rectangle((20, 50, 236, 130), fill=(255, 200, 60))
    d.rectangle((30, 58, 100, 110), fill=(30, 40, 70))
    d.rectangle((150, 58, 226, 110), fill=(30, 40, 70))
    d.rectangle((0, 160, 255, 223), fill=(12, 12, 16))
    d.rectangle((0, 150, 255, 158), fill=(255, 80, 80))
    return im


def _platform() -> Image.Image:
    im, d = new_scene((22, 24, 40))
    d.rectangle((0, 80, 255, 120), fill=(255, 220, 80))
    d.rectangle((0, 120, 255, 180), fill=(50, 54, 70))
    d.rectangle((80, 20, 176, 80), fill=(20, 180, 120))
    d.rectangle((0, 180, 255, 223), fill=(16, 16, 24))
    d.rectangle((0, 176, 255, 182), fill=(255, 255, 255))
    return im


def _rooftop() -> Image.Image:
    im, d = new_scene((255, 186, 140))
    d.rectangle((0, 0, 255, 90), fill=(255, 214, 170))
    d.ellipse((170, 16, 230, 76), fill=(255, 244, 200))
    for x in range(10, 240, 18):
        d.rectangle((x, 90, x + 4, 140), fill=(80, 70, 90))
    d.rectangle((0, 140, 255, 223), fill=(90, 70, 96))
    d.rectangle((0, 140, 255, 148), fill=(255, 120, 160))
    return im


def _eyes(d: ImageDraw.ImageDraw, y: int = 30) -> None:
    d.ellipse((26, y, 32, y + 6), fill=(40, 24, 24))
    d.ellipse((40, y, 46, y + 6), fill=(40, 24, 24))
    d.point((28, y + 2), fill=(255, 255, 255))
    d.point((42, y + 2), fill=(255, 255, 255))


def _fallback_portrait(name: str) -> Image.Image:
    im = Image.new("RGBA", SNES_PORTRAIT, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "linxia":
        d.ellipse((18, 14, 54, 56), fill=(255, 214, 180))
        d.pieslice((12, 4, 60, 48), 180, 360, fill=(28, 20, 18))
        d.polygon([(12, 24), (6, 58), (20, 44)], fill=(28, 20, 18))
        d.polygon([(60, 24), (66, 58), (52, 44)], fill=(28, 20, 18))
        _eyes(d, 30)
        d.arc((30, 36, 42, 46), 20, 160, fill=(180, 80, 90), width=2)
        d.rectangle((20, 54, 52, 94), fill=(255, 208, 46))
        d.rectangle((26, 54, 46, 72), fill=(255, 72, 96))
        d.polygon([(26, 54), (36, 78), (46, 54)], fill=(255, 72, 96))
    elif name == "qing":
        d.ellipse((18, 16, 54, 56), fill=(255, 224, 196))
        d.pieslice((14, 6, 58, 40), 180, 360, fill=(32, 210, 176))
        d.rectangle((14, 18, 58, 28), fill=(32, 210, 176))
        d.ellipse((6, 24, 20, 40), fill=(24, 24, 30))
        d.ellipse((52, 24, 66, 40), fill=(24, 24, 30))
        d.ellipse((8, 26, 18, 36), fill=(60, 255, 210))
        d.ellipse((54, 26, 64, 36), fill=(60, 255, 210))
        _eyes(d, 32)
        d.line((32, 42, 40, 42), fill=(160, 90, 90), width=2)
        d.rectangle((22, 56, 50, 94), fill=(248, 248, 255))
        d.rectangle((22, 74, 50, 94), fill=(18, 18, 28))
        d.rectangle((20, 56, 52, 62), fill=(32, 210, 176))
    elif name == "zhou":
        d.ellipse((16, 18, 56, 60), fill=(226, 184, 148))
        d.rectangle((14, 12, 58, 26), fill=(72, 44, 32))
        d.rectangle((12, 20, 18, 36), fill=(72, 44, 32))
        _eyes(d, 34)
        d.arc((28, 40, 44, 52), 200, 340, fill=(90, 50, 40), width=2)
        d.rectangle((14, 58, 58, 94), fill=(168, 52, 40))
        d.rectangle((24, 58, 48, 76), fill=(230, 210, 190))
        d.rectangle((22, 76, 50, 80), fill=(40, 28, 24))
    elif name == "hai":
        d.ellipse((18, 16, 54, 56), fill=(255, 220, 186))
        d.pieslice((14, 4, 58, 36), 180, 360, fill=(48, 92, 230))
        d.polygon([(14, 20), (10, 40), (22, 32)], fill=(48, 92, 230))
        _eyes(d, 30)
        d.ellipse((34, 40, 38, 44), fill=(80, 40, 40))
        d.rectangle((20, 56, 52, 94), fill=(16, 196, 176))
        d.rectangle((28, 58, 44, 72), fill=(255, 148, 48))
        d.rectangle((18, 88, 54, 94), fill=(12, 80, 90))
    elif name == "clerk":
        d.ellipse((18, 18, 54, 56), fill=(240, 200, 160))
        d.rectangle((14, 10, 58, 24), fill=(36, 170, 86))
        d.polygon([(14, 24), (36, 8), (58, 24)], fill=(36, 170, 86))
        _eyes(d, 32)
        d.rectangle((20, 56, 52, 94), fill=(48, 210, 96))
        d.rectangle((20, 56, 52, 68), fill=(255, 230, 70))
        d.rectangle((32, 68, 40, 86), fill=(255, 250, 220))
    else:
        d.ellipse((18, 16, 54, 54), fill=(80, 40, 120))
        d.rectangle((22, 54, 50, 94), fill=(40, 20, 60))
    return im


def paint_portrait(name: str, size: tuple[int, int] = SNES_PORTRAIT) -> Image.Image:
    src = None
    png = PORTRAIT_DIR / f"{name}.png"
    if png.exists():
        src = Image.open(png).convert("RGBA")
    else:
        rgb = _open_rgb(PORTRAIT_DIR / f"{name}.jpg")
        if rgb is not None:
            src = rgb.convert("RGBA")
    if src is None:
        fb = _fallback_portrait(name)
        if fb.size == size:
            return fb
        return fb.resize(size, Image.Resampling.NEAREST).convert("RGBA")
    return _cover(src, size).convert("RGBA")


def paint_portrait_web(name: str) -> Image.Image:
    return paint_portrait(name, WEB_PORTRAIT)


def all_scene_names() -> list[str]:
    return [
        "title",
        "apartment",
        "elevator",
        "street_rain",
        "store",
        "overpass",
        "mall",
        "tape_shop",
        "tape_back",
        "aquarium",
        "tank",
        "pump",
        "bus",
        "subway",
        "platform",
        "rooftop",
        "hutong",
        "avenue",
        "xidan_road",
        "aqua_road",
        "dawn_apt",
        "mall_mid",
        "aqua_tunnel",
        "riverbank",
        "nameless_lane",
        "metro_gate",
        "gap_tunnel",
        "pale_dawn",
        "morning_st",
        "home_rain",
        "duty_room",
        "wave_plat",
    ]


def all_portrait_names() -> list[str]:
    return ["linxia", "qing", "zhou", "hai", "clerk"]
