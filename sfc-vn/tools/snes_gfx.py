"""SFC 4bpp 字库、场景与调色板。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
SCREEN_W = 256
SCREEN_H = 224
TILE = 8


def rgb_to_bgr15(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def pack_palette(colors: list[tuple[int, int, int]], n: int = 16) -> bytes:
    out = bytearray()
    for i in range(n):
        color = colors[i] if i < len(colors) else (0, 0, 0)
        value = rgb_to_bgr15(color)
        out.extend((value & 0xFF, (value >> 8) & 0xFF))
    return bytes(out)


def encode_tile_4bpp(pixels: list[int]) -> bytes:
    """pixels: 64 values 0-15, row-major."""
    out = bytearray(32)
    for y in range(8):
        p0 = p1 = p2 = p3 = 0
        for x in range(8):
            pix = pixels[y * 8 + x] & 15
            bit = 7 - x
            p0 |= ((pix >> 0) & 1) << bit
            p1 |= ((pix >> 1) & 1) << bit
            p2 |= ((pix >> 2) & 1) << bit
            p3 |= ((pix >> 3) & 1) << bit
        out[y * 2] = p0
        out[y * 2 + 1] = p1
        out[16 + y * 2] = p2
        out[16 + y * 2 + 1] = p3
    return bytes(out)


def decode_tile_4bpp(data: bytes) -> list[int]:
    pixels = [0] * 64
    for y in range(8):
        p0, p1 = data[y * 2], data[y * 2 + 1]
        p2, p3 = data[16 + y * 2], data[16 + y * 2 + 1]
        for x in range(8):
            bit = 7 - x
            pix = (
                ((p0 >> bit) & 1)
                | (((p1 >> bit) & 1) << 1)
                | (((p2 >> bit) & 1) << 2)
                | (((p3 >> bit) & 1) << 3)
            )
            pixels[y * 8 + x] = pix
    return pixels


def render_glyph(ch: str, font: ImageFont.FreeTypeFont) -> list[int]:
    im = Image.new("L", (16, 16), 0)
    draw = ImageDraw.Draw(im)
    bbox = draw.textbbox((0, 0), ch, font=font)
    gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = max(0, (16 - gw) // 2 - bbox[0])
    y = max(0, (16 - gh) // 2 - bbox[1])
    draw.text((x, y), ch, font=font, fill=255)
    pixels: list[int] = []
    for py in range(16):
        for px in range(16):
            v = im.getpixel((px, py))
            if v > 180:
                pixels.append(4)
            elif v > 80:
                pixels.append(3)
            else:
                pixels.append(0)
    return pixels


def glyph_to_tiles(pixels16: list[int]) -> bytes:
    tiles = bytearray()
    for ty in (0, 1):
        for tx in (0, 1):
            raw = []
            for y in range(8):
                for x in range(8):
                    raw.append(pixels16[(ty * 8 + y) * 16 + (tx * 8 + x)])
            tiles.extend(encode_tile_4bpp(raw))
    return bytes(tiles)


def make_font_tiles(charset: list[str]) -> tuple[bytes, dict[str, int]]:
    font = ImageFont.truetype(str(FONT_PATH), 14)
    mapping: dict[str, int] = {}
    blob = bytearray()
    for ch in charset:
        mapping[ch] = len(blob) // 128
        blob.extend(glyph_to_tiles(render_glyph(ch, font)))
    # UI tiles after glyphs: 4bpp 8x8
    ui = {
        "blank": [0] * 64,
        "box": [1] * 64,
        "bar": [2 if y in (0, 7) else 1 for y in range(8) for _ in range(8)],
        "cursor": render_ui_cursor(),
    }
    ui_index = {}
    for name, pixels in ui.items():
        ui_index[name] = len(blob) // 32
        blob.extend(encode_tile_4bpp(pixels))
    return bytes(blob), mapping | {f"ui:{k}": v for k, v in ui_index.items()}


def render_ui_cursor() -> list[int]:
    mask = [
        "10000000",
        "11000000",
        "11100000",
        "11110000",
        "11100000",
        "11000000",
        "10000000",
        "00000000",
    ]
    pixels = []
    for row in mask:
        for ch in row:
            pixels.append(5 if ch == "1" else 0)
    return pixels


TEXT_PALETTE = [
    (0, 0, 0),
    (12, 18, 48),
    (196, 156, 72),
    (220, 200, 150),
    (248, 244, 230),
    (255, 212, 96),
    (40, 50, 90),
    (90, 70, 40),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
]


def _put(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
    draw.rectangle(xy, fill=color)


def paint_scene(name: str) -> Image.Image:
    im = Image.new("RGB", (SCREEN_W, SCREEN_H), (8, 10, 28))
    d = ImageDraw.Draw(im)
    if name == "title":
        _paint_title(d)
    elif name == "post":
        _paint_post(d)
    elif name == "street":
        _paint_street(d)
    elif name == "bridge":
        _paint_bridge(d)
    elif name == "home":
        _paint_home(d)
    elif name == "lantern":
        _paint_lantern(d)
    else:
        _paint_bridge(d)
    return im


def _paint_title(d: ImageDraw.ImageDraw) -> None:
    _put(d, (0, 0, 255, 223), (6, 10, 32))
    d.ellipse((176, 18, 214, 56), fill=(236, 220, 150))
    d.ellipse((184, 22, 208, 46), fill=(246, 236, 190))
    _put(d, (0, 148, 255, 200), (16, 28, 72))
    d.polygon([(0, 168), (255, 148), (255, 162), (0, 182)], fill=(52, 38, 32))
    d.line([(20, 160), (240, 144)], fill=(90, 64, 48), width=2)


def _paint_post(d: ImageDraw.ImageDraw) -> None:
    _put(d, (0, 0, 255, 223), (42, 28, 22))
    _put(d, (0, 0, 255, 70), (18, 16, 40))
    _put(d, (20, 18, 118, 78), (12, 14, 36))
    d.ellipse((74, 28, 104, 58), fill=(232, 214, 140))
    _put(d, (20, 78, 236, 88), (90, 62, 40))
    _put(d, (28, 100, 228, 150), (72, 48, 34))
    _put(d, (40, 112, 100, 138), (30, 22, 18))
    _put(d, (150, 108, 210, 146), (120, 86, 50))
    d.rectangle((168, 118, 196, 136), outline=(200, 170, 90))
    _put(d, (0, 168, 255, 223), (28, 20, 16))


def _paint_street(d: ImageDraw.ImageDraw) -> None:
    _put(d, (0, 0, 255, 140), (8, 12, 36))
    _put(d, (0, 140, 255, 223), (36, 32, 40))
    d.ellipse((190, 16, 222, 48), fill=(236, 220, 150))
    _put(d, (0, 88, 70, 160), (48, 36, 44))
    _put(d, (12, 60, 62, 88), (90, 40, 36))
    _put(d, (80, 96, 148, 168), (40, 32, 46))
    _put(d, (94, 112, 114, 132), (200, 150, 70))
    _put(d, (170, 84, 255, 176), (34, 28, 40))
    _put(d, (186, 104, 210, 128), (180, 130, 60))
    d.polygon([(0, 168), (255, 150), (255, 223), (0, 223)], fill=(28, 26, 34))


def _paint_bridge(d: ImageDraw.ImageDraw) -> None:
    _put(d, (0, 0, 255, 223), (7, 12, 34))
    d.ellipse((168, 14, 208, 54), fill=(240, 224, 156))
    _put(d, (0, 150, 255, 200), (18, 32, 78))
    for x in range(0, 256, 10):
        d.line([(x, 156), (x + 6, 164)], fill=(40, 60, 110))
    d.polygon([(0, 166), (255, 146), (255, 160), (0, 180)], fill=(58, 42, 36))
    d.line([(8, 158), (248, 140)], fill=(120, 84, 56), width=3)
    for x in range(24, 240, 28):
        d.line([(x, 132), (x, 162)], fill=(92, 64, 48), width=2)
    d.ellipse((120, 118, 132, 136), fill=(20, 16, 18))
    d.ellipse((188, 112, 198, 128), fill=(230, 226, 220))


def _paint_home(d: ImageDraw.ImageDraw) -> None:
    _put(d, (0, 0, 255, 223), (58, 36, 24))
    _put(d, (0, 0, 255, 64), (20, 16, 32))
    _put(d, (16, 16, 96, 68), (10, 12, 28))
    d.ellipse((44, 24, 72, 52), fill=(236, 210, 130))
    _put(d, (140, 72, 172, 150), (40, 24, 18))
    _put(d, (148, 40, 164, 72), (80, 48, 28))
    d.ellipse((132, 28, 180, 48), fill=(255, 170, 70))
    _put(d, (20, 150, 130, 190), (90, 58, 36))
    d.ellipse((168, 128, 200, 150), fill=(240, 120, 60))
    _put(d, (0, 196, 255, 223), (40, 26, 20))


def _paint_lantern(d: ImageDraw.ImageDraw) -> None:
    _put(d, (0, 0, 255, 223), (10, 14, 30))
    _put(d, (0, 160, 255, 210), (14, 24, 50))
    d.ellipse((20, 20, 48, 48), fill=(180, 186, 210))
    d.polygon([(40, 180), (220, 150), (255, 170), (255, 200), (0, 210)], fill=(20, 22, 40))
    d.ellipse((118, 88, 148, 128), fill=(255, 150, 50))
    d.ellipse((124, 96, 142, 120), fill=(255, 220, 120))
    d.line([(133, 70), (133, 90)], fill=(180, 140, 70), width=2)
    d.ellipse((200, 100, 214, 122), fill=(40, 36, 48))


def image_to_tiles(
    im: Image.Image, max_tiles: int = 240
) -> tuple[bytes, bytes, list[tuple[int, int, int]]]:
    quantized = im.convert("P", palette=Image.Palette.ADAPTIVE, colors=15)
    palette_raw = list(quantized.getpalette() or [])
    colors = [(0, 0, 0)]
    for i in range(15):
        base = i * 3
        if base + 2 < len(palette_raw):
            colors.append((palette_raw[base], palette_raw[base + 1], palette_raw[base + 2]))
        else:
            colors.append((0, 0, 0))
    # remap 0-14 -> 1-15 so 0 stays unused/black
    px = quantized.load()
    unique: dict[tuple[int, ...], int] = {}
    tiles = bytearray()
    map_words: list[int] = []
    for ty in range(28):
        for tx in range(32):
            key_pixels = []
            idx_pixels = []
            for y in range(8):
                for x in range(8):
                    src = px[tx * 8 + x, ty * 8 + y]
                    color_index = src + 1
                    key_pixels.append(color_index)
                    idx_pixels.append(color_index)
            key = tuple(key_pixels)
            if key not in unique:
                if len(unique) >= max_tiles:
                    # collapse extras into tile 0
                    unique[key] = 0
                else:
                    unique[key] = len(unique)
                    tiles.extend(encode_tile_4bpp(idx_pixels))
            map_words.append(unique[key])
    while len(map_words) < 32 * 32:
        map_words.append(0)
    tilemap = bytearray()
    for word in map_words:
        tilemap.extend((word & 0xFF, (word >> 8) & 0xFF))
    return bytes(tiles), bytes(tilemap), colors


def encode_tilemap_words(words: list[int]) -> bytes:
    out = bytearray()
    for word in words:
        out.extend((word & 0xFF, (word >> 8) & 0xFF))
    return bytes(out)


def put_string(
    words: list[int],
    mapping: dict[str, int],
    x: int,
    y: int,
    text: str,
    *,
    attr: int,
) -> None:
    tx = x
    for ch in text:
        glyph = mapping.get(ch, mapping.get("　"))
        if glyph is None:
            continue
        base = glyph * 4
        for dx, dy, add in ((0, 0, 0), (1, 0, 1), (0, 1, 2), (1, 1, 3)):
            px, py = tx + dx, y + dy
            if 0 <= px < 32 and 0 <= py < 32:
                words[py * 32 + px] = (base + add) | attr
        tx += 2
        if tx > 29:
            break


def make_text_tilemap(
    lines: list[str],
    mapping: dict[str, int],
    *,
    cursor_row: int | None = None,
    overlays: list[tuple[int, int, str]] | None = None,
    draw_box: bool = True,
) -> list[int]:
    """32x32 tilemap words for BG2. Text box occupies rows 18-27."""
    blank = mapping["ui:blank"]
    box = mapping["ui:box"]
    bar = mapping["ui:bar"]
    words = [blank] * (32 * 32)
    attr = (1 << 10) | (1 << 13)

    def put_tile(x: int, y: int, tile: int) -> None:
        if 0 <= x < 32 and 0 <= y < 32:
            words[y * 32 + x] = tile | attr

    if draw_box:
        for y in range(18, 28):
            for x in range(32):
                put_tile(x, y, bar if y in (18, 27) else box)
        for row, line in enumerate(lines[:4]):
            ty = 19 + row * 2
            if cursor_row is not None and row == cursor_row:
                put_tile(1, ty, mapping["ui:cursor"])
                put_tile(1, ty + 1, mapping["ui:blank"])
            put_string(words, mapping, 2, ty, line, attr=attr)
    for ox, oy, text in overlays or []:
        put_string(words, mapping, ox, oy, text, attr=attr)
    return words
