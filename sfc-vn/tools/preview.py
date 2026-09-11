#!/usr/bin/env python3
"""用同一套资源画出软件预览，并用迷你模拟器导出 ROM 帧。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.story import STORY, TITLE_HINT, ChoiceNode, EndingNode, TextNode, collect_charset
from tools.build_rom import build_rom
from tools.mini_snes import CPU, pixels_to_ppm, render_frame
from tools.snes_gfx import (
    SCREEN_H,
    SCREEN_W,
    TEXT_PALETTE,
    decode_tile_4bpp,
    make_font_tiles,
    make_text_tilemap,
    paint_scene,
)


def composite_preview(
    scene: str,
    lines: list[str],
    mapping: dict[str, int],
    font_blob: bytes,
    cursor: int | None = None,
    overlays: list[tuple[int, int, str]] | None = None,
) -> Image.Image:
    bg = paint_scene(scene).convert("RGB")
    words = make_text_tilemap(lines, mapping, cursor_row=cursor, overlays=overlays)
    box = Image.new("RGBA", (SCREEN_W, SCREEN_H), (0, 0, 0, 0))
    pixels = box.load()

    def tile_img(tile: int) -> list[int]:
        off = tile * 32
        return decode_tile_4bpp(font_blob[off : off + 32])

    for ty in range(32):
        for tx in range(32):
            word = words[ty * 32 + tx]
            tile = word & 0x3FF
            pix = tile_img(tile)
            for y in range(8):
                for x in range(8):
                    color = pix[y * 8 + x]
                    if color == 0:
                        continue
                    rgb = TEXT_PALETTE[color]
                    px, py = tx * 8 + x, ty * 8 + y
                    if py < SCREEN_H:
                        pixels[px, py] = (*rgb, 255)
    return Image.alpha_composite(bg.convert("RGBA"), box).convert("RGB")


def save_story_previews(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    font_blob, mapping = make_font_tiles(collect_charset())
    paths: list[Path] = []
    title = composite_preview(
        "title",
        ["", "", "", TITLE_HINT],
        mapping,
        font_blob,
        overlays=[(13, 8, "月见桥"), (8, 12, "一封没有名字的信")],
    )
    path = out_dir / "preview_title.png"
    title.save(path)
    paths.append(path)
    for name, node in STORY.items():
        if isinstance(node, TextNode):
            im = composite_preview(node.scene, list(node.lines), mapping, font_blob)
        elif isinstance(node, ChoiceNode):
            lines = [node.prompt, *(text for text, _ in node.options)]
            im = composite_preview(node.scene, lines, mapping, font_blob, cursor=1)
        else:
            im = composite_preview(node.scene, [node.title, *node.lines[:3]], mapping, font_blob)
        path = out_dir / f"preview_{name}.png"
        im.save(path)
        paths.append(path)
    return paths


def hold_until(cpu: CPU, pred, limit: int = 200_000) -> None:
    start = cpu.steps
    while cpu.steps - start < limit and not cpu.halted and not pred(cpu):
        cpu.run(400)


def dump_rom_frames(rom: bytes, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cpu = CPU(rom)
    cpu.reset()
    hold_until(cpu, lambda c: (c.inidisp & 0x80) == 0 and c.tm == 3)
    paths = []

    def snap(name: str) -> Path:
        pixels = render_frame(cpu)
        ppm = out_dir / f"{name}.ppm"
        png = out_dir / f"{name}.png"
        pixels_to_ppm(pixels, str(ppm))
        Image.frombytes("RGB", (256, 224), bytes(c for p in pixels for c in p)).save(png)
        ppm.unlink(missing_ok=True)
        return png

    paths.append(snap("rom_title"))
    cpu.joy = 0x1000  # Start down
    cpu.run(2000)
    cpu.joy = 0
    cpu.run(4000)
    paths.append(snap("rom_after_start"))
    for i in range(4):
        cpu.joy = 0x0080  # A
        cpu.run(2000)
        cpu.joy = 0
        cpu.run(3000)
        paths.append(snap(f"rom_page_{i}"))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", type=Path, default=ROOT / "dist" / "preview")
    args = parser.parse_args()
    save_story_previews(args.out)
    rom = build_rom()
    (ROOT / "dist" / "yuejianqiao.sfc").write_bytes(rom)
    dump_rom_frames(rom, args.out)
    print(f"preview written to {args.out}")


if __name__ == "__main__":
    main()
