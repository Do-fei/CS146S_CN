#!/usr/bin/env python3
"""把剧本、字库和 65816 引擎组装成 LoROM .sfc。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.story import (  # noqa: E402
    START_NODE,
    STORY,
    TITLE_HINT,
    ChoiceNode,
    EndingNode,
    TextNode,
    collect_charset,
    story_graph_errors,
)
from tools.asm65816 import Asm, lorom_offset  # noqa: E402
from tools.snes_gfx import (  # noqa: E402
    TEXT_PALETTE,
    encode_tilemap_words,
    image_to_tiles,
    make_font_tiles,
    make_text_tilemap,
    pack_palette,
    paint_scene,
)

ROM_SIZE = 256 * 1024
SCENE_NAMES = ["title", "post", "street", "bridge", "home", "lantern"]
SCENE_TILE_BYTES = 240 * 32
OP_SCENE = 1
OP_TEXT = 2
OP_CHOICE = 3
OP_END = 4
OP_JUMP = 5

NMI = 0x00
JOY_RAW = 0x02
JOY_PREV = 0x04
JOY_NEW = 0x06
SCRIPT = 0x08
TMP = 0x0C
SRC = 0x14
CHOICE_N = 0x20
CHOICE_I = 0x21
CHOICE_DATA = 0x22


def write_header(rom: bytearray, title: str) -> None:
    name = title.encode("ascii", "replace")[:21]
    name = name + b" " * (21 - len(name))
    base = lorom_offset(0x80, 0xFFC0)
    rom[base : base + 21] = name
    rom[lorom_offset(0x80, 0xFFD5)] = 0x20
    rom[lorom_offset(0x80, 0xFFD6)] = 0x00
    rom[lorom_offset(0x80, 0xFFD7)] = 0x08
    rom[lorom_offset(0x80, 0xFFD8)] = 0x00
    rom[lorom_offset(0x80, 0xFFD9)] = 0x00
    rom[lorom_offset(0x80, 0xFFDA)] = 0x00
    rom[lorom_offset(0x80, 0xFFDB)] = 0x00
    write_checksum(rom)


def write_checksum(rom: bytearray) -> None:
    csum_off = lorom_offset(0x80, 0xFFDC)
    rom[csum_off : csum_off + 4] = b"\x00\x00\x00\x00"
    rest = sum(rom) & 0xFFFF
    checksum = (rest + 0x01FE) & 0xFFFF
    complement = checksum ^ 0xFFFF
    rom[csum_off] = complement & 0xFF
    rom[csum_off + 1] = (complement >> 8) & 0xFF
    rom[csum_off + 2] = checksum & 0xFF
    rom[csum_off + 3] = (checksum >> 8) & 0xFF


def write_vectors(a: Asm) -> None:
    def vec(addr: int, label: str) -> None:
        _bank, pc = a.labels[label]
        off = lorom_offset(0x80, addr)
        a.rom[off] = pc & 0xFF
        a.rom[off + 1] = (pc >> 8) & 0xFF

    for slot in (0xFFEA, 0xFFFA, 0xFFEE, 0xFFFE, 0xFFE6, 0xFFE8):
        vec(slot, "nmi")
    vec(0xFFFC, "reset")
    vec(0xFFEC, "reset")


def emit_engine(a: Asm) -> None:
    """A 默认 8 位，X/Y 默认 16 位。"""
    a.org(0x80, 0x8000)
    a.label("reset")
    a.sei()
    a.clc()
    a.xce()
    a.rep(0x30)
    a.ldx_imm(0x1FFF)
    a.txs()
    a.lda_imm(0x0000)
    a.tcd()
    a.phk()
    a.plb()
    a.sep(0x20)
    a.rep(0x10)
    a.lda_imm(0x8F)
    a.sta_abs(0x2100)
    a.stz_abs(0x4200)
    a.stz_abs(0x420B)
    a.stz_abs(0x420C)
    a.lda_imm(0x01)
    a.sta_abs(0x2105)
    a.lda_imm(0x10)
    a.sta_abs(0x2107)
    a.lda_imm(0x14)
    a.sta_abs(0x2108)
    a.lda_imm(0x20)
    a.sta_abs(0x210B)
    a.lda_imm(0x03)
    a.sta_abs(0x212C)
    a.stz_abs(0x212D)
    a.stz_abs(0x2130)
    a.stz_abs(0x2131)
    a.lda_imm(0xE0)
    a.sta_abs(0x2132)
    a.stz_abs(0x2101)
    for reg in (0x210D, 0x210E, 0x210F, 0x2110, 0x2111, 0x2112, 0x2113, 0x2114):
        a.stz_abs(reg)
        a.stz_abs(reg)
    a.lda_imm(0x80)
    a.sta_abs(0x2115)
    a.stz_dp(NMI)
    a.rep(0x20)
    a.stz_dp(JOY_RAW)
    a.stz_dp(JOY_PREV)
    a.stz_dp(JOY_NEW)
    a.sep(0x20)
    a.jsr("dma_font")
    a.jsr("dma_text_palette")
    a.lda_imm(0x81)
    a.sta_abs(0x4200)
    a.jsr("wait_nmi")
    a.jsr("wait_nmi")

    a.label("title")
    a.lda_imm(0x8F)
    a.sta_abs(0x2100)
    a.lda_imm(0x00)
    a.jsr("load_scene")
    a.rep(0x20)
    a.lda_imm(0x0000)
    a.sta_dp(TMP)
    a.sep(0x20)
    a.jsr("load_page")
    a.lda_imm(0x0F)
    a.sta_abs(0x2100)
    a.label("title_loop")
    a.jsr("wait_nmi")
    a.jsr("read_joy")
    a.lda_dp(JOY_NEW + 1)
    a.and_imm(0x10)
    a.beq("title_loop")
    a.lda_abs("script_entry")
    a.sta_dp(SCRIPT)
    a.lda_abs("script_entry_hi")
    a.sta_dp(SCRIPT + 1)
    a.lda_abs("script_entry_bk")
    a.sta_dp(SCRIPT + 2)

    a.label("interp")
    a.jsr("read_script_byte")
    a.cmp_imm(OP_SCENE)
    a.beq("do_scene")
    a.cmp_imm(OP_TEXT)
    a.beq("do_text")
    a.cmp_imm(OP_CHOICE)
    a.beq("do_choice")
    a.cmp_imm(OP_END)
    a.beq("do_end")
    a.cmp_imm(OP_JUMP)
    a.beq("do_jump")
    a.jmp("title")

    a.label("do_scene")
    a.jsr("read_script_byte")
    a.jsr("load_scene")
    a.jmp("interp")

    a.label("do_text")
    a.jsr("read_script_u16_tmp")
    a.jsr("load_page")
    a.jsr("wait_button_a")
    a.jmp("interp")

    a.label("do_end")
    a.jsr("read_script_u16_tmp")
    a.jsr("load_page")
    a.jsr("wait_button_a")
    a.jmp("title")

    a.label("do_jump")
    a.jsr("read_script_byte")
    a.sta_dp(TMP)
    a.jsr("read_script_byte")
    a.sta_dp(TMP + 1)
    a.jsr("read_script_byte")
    a.sta_dp(TMP + 2)
    a.lda_dp(TMP)
    a.sta_dp(SCRIPT)
    a.lda_dp(TMP + 1)
    a.sta_dp(SCRIPT + 1)
    a.lda_dp(TMP + 2)
    a.sta_dp(SCRIPT + 2)
    a.jmp("interp")

    a.label("do_choice")
    a.jsr("read_script_byte")
    a.sta_dp(0x1F)
    a.sta_dp(CHOICE_N)
    a.stz_dp(CHOICE_I)
    a.ldy_imm(0x0000)
    a.label("choice_copy_opt")
    a.ldx_imm(0x0005)
    a.label("choice_copy_byte")
    a.jsr("read_script_byte")
    a.sta_absy(CHOICE_DATA)
    a.iny()
    a.dex()
    a.bne("choice_copy_byte")
    a.dec_dp(CHOICE_N)
    a.bne("choice_copy_opt")
    a.lda_dp(0x1F)
    a.sta_dp(CHOICE_N)

    a.label("choice_show")
    a.jsr("choice_page_to_tmp")
    a.jsr("load_page")
    a.label("choice_wait")
    a.jsr("wait_nmi")
    a.jsr("read_joy")
    a.lda_dp(JOY_NEW + 1)
    a.and_imm(0x08)
    a.beq("choice_not_up")
    a.lda_dp(CHOICE_I)
    a.beq("choice_wait")
    a.dec_dp(CHOICE_I)
    a.jmp("choice_show")
    a.label("choice_not_up")
    a.lda_dp(JOY_NEW + 1)
    a.and_imm(0x04)
    a.beq("choice_not_down")
    a.lda_dp(CHOICE_I)
    a.inc_a()
    a.cmp_dp(CHOICE_N)
    a.bcs("choice_wait")
    a.sta_dp(CHOICE_I)
    a.jmp("choice_show")
    a.label("choice_not_down")
    a.lda_dp(JOY_NEW)
    a.and_imm(0x80)
    a.beq("choice_wait")
    a.jsr("choice_dest_to_script")
    a.jmp("interp")

    a.label("choice_page_to_tmp")
    a.lda_dp(CHOICE_I)
    a.sta_dp(TMP)
    a.asl_a()
    a.asl_a()
    a.clc()
    a.adc_dp(TMP)
    a.tax()
    a.lda_absx(CHOICE_DATA)
    a.sta_dp(TMP)
    a.inx()
    a.lda_absx(CHOICE_DATA)
    a.sta_dp(TMP + 1)
    a.rts()

    a.label("choice_dest_to_script")
    a.lda_dp(CHOICE_I)
    a.sta_dp(TMP)
    a.asl_a()
    a.asl_a()
    a.clc()
    a.adc_dp(TMP)
    a.clc()
    a.adc_imm(0x02)
    a.tax()
    a.lda_absx(CHOICE_DATA)
    a.sta_dp(SCRIPT)
    a.inx()
    a.lda_absx(CHOICE_DATA)
    a.sta_dp(SCRIPT + 1)
    a.inx()
    a.lda_absx(CHOICE_DATA)
    a.sta_dp(SCRIPT + 2)
    a.rts()

    a.label("read_script_u16_tmp")
    a.jsr("read_script_byte")
    a.sta_dp(TMP)
    a.jsr("read_script_byte")
    a.sta_dp(TMP + 1)
    a.rts()

    a.label("read_script_byte")
    a.lda_il(SCRIPT)
    a.pha()
    a.inc_dp(SCRIPT)
    a.bne("rsb_done")
    a.inc_dp(SCRIPT + 1)
    a.bne("rsb_done")
    a.inc_dp(SCRIPT + 2)
    a.label("rsb_done")
    a.pla()
    a.rts()

    a.label("wait_nmi")
    a.label("wait_nmi_loop")
    a.lda_dp(NMI)
    a.beq("wait_nmi_loop")
    a.stz_dp(NMI)
    a.rts()

    a.label("read_joy")
    a.label("read_joy_busy")
    a.lda_abs(0x4212)
    a.lsr_a()
    a.bcs("read_joy_busy")
    a.rep(0x20)
    a.lda_abs(0x4218)
    a.sta_dp(JOY_RAW)
    a.eor_dp(JOY_PREV)
    a.and_dp(JOY_RAW)
    a.sta_dp(JOY_NEW)
    a.lda_dp(JOY_RAW)
    a.sta_dp(JOY_PREV)
    a.sep(0x20)
    a.rts()

    a.label("wait_button_a")
    a.label("wait_a_loop")
    a.jsr("wait_nmi")
    a.jsr("read_joy")
    a.lda_dp(JOY_NEW)
    a.and_imm(0x80)
    a.beq("wait_a_loop")
    a.rts()

    a.label("load_scene")
    a.sta_dp(0x0E)
    a.stz_dp(0x0F)
    a.rep(0x20)
    a.lda_dp(0x0E)
    a.asl_a()
    a.clc()
    a.adc_dp(0x0E)
    a.tax()
    a.sep(0x20)
    a.lda_absx("scene_table")
    a.sta_dp(SRC)
    a.inx()
    a.lda_absx("scene_table")
    a.sta_dp(SRC + 1)
    a.inx()
    a.lda_absx("scene_table")
    a.sta_dp(SRC + 2)
    a.ldx_imm(0x0000)
    a.ldy_imm(SCENE_TILE_BYTES)
    a.jsr("dma_vram")
    a.jsr("add_src_tiles")
    a.ldx_imm(0x1000)
    a.ldy_imm(0x0800)
    a.jsr("dma_vram")
    a.jsr("add_src_map")
    a.lda_imm(0x00)
    a.sta_abs(0x2121)
    a.stz_abs(0x4300)
    a.lda_imm(0x22)
    a.sta_abs(0x4301)
    a.lda_dp(SRC)
    a.sta_abs(0x4302)
    a.lda_dp(SRC + 1)
    a.sta_abs(0x4303)
    a.lda_dp(SRC + 2)
    a.sta_abs(0x4304)
    a.ldx_imm(0x0020)
    a.stx_abs(0x4305)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    a.rts()

    a.label("load_page")
    a.rep(0x20)
    a.lda_dp(TMP)
    a.asl_a()
    a.clc()
    a.adc_dp(TMP)
    a.tax()
    a.sep(0x20)
    a.lda_absx("page_table")
    a.sta_dp(SRC)
    a.inx()
    a.lda_absx("page_table")
    a.sta_dp(SRC + 1)
    a.inx()
    a.lda_absx("page_table")
    a.sta_dp(SRC + 2)
    a.ldx_imm(0x1400)
    a.ldy_imm(0x0800)
    a.jsr("dma_vram")
    a.rts()

    a.label("add_src_tiles")
    a.rep(0x20)
    a.lda_dp(SRC)
    a.clc()
    a.adc_imm(SCENE_TILE_BYTES)
    a.sta_dp(SRC)
    a.sep(0x20)
    a.bcc("add_src_tiles_ok")
    a.inc_dp(SRC + 2)
    a.label("add_src_tiles_ok")
    a.rts()

    a.label("add_src_map")
    a.rep(0x20)
    a.lda_dp(SRC)
    a.clc()
    a.adc_imm(0x0800)
    a.sta_dp(SRC)
    a.sep(0x20)
    a.bcc("add_src_map_ok")
    a.inc_dp(SRC + 2)
    a.label("add_src_map_ok")
    a.rts()

    a.label("dma_vram")
    a.lda_imm(0x80)
    a.sta_abs(0x2115)
    a.stx_abs(0x2116)
    a.lda_imm(0x01)
    a.sta_abs(0x4300)
    a.lda_imm(0x18)
    a.sta_abs(0x4301)
    a.lda_dp(SRC)
    a.sta_abs(0x4302)
    a.lda_dp(SRC + 1)
    a.sta_abs(0x4303)
    a.lda_dp(SRC + 2)
    a.sta_abs(0x4304)
    a.sty_abs(0x4305)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    a.rts()

    a.label("dma_font")
    a.lda_abs("font_ptr")
    a.sta_dp(SRC)
    a.lda_abs("font_ptr_hi")
    a.sta_dp(SRC + 1)
    a.lda_abs("font_ptr_bk")
    a.sta_dp(SRC + 2)
    a.ldx_imm(0x2000)
    a.ldy_abs("font_size")
    a.jsr("dma_vram")
    a.rts()

    a.label("dma_text_palette")
    a.lda_imm(0x10)
    a.sta_abs(0x2121)
    a.lda_abs("textpal_ptr")
    a.sta_dp(SRC)
    a.lda_abs("textpal_ptr_hi")
    a.sta_dp(SRC + 1)
    a.lda_abs("textpal_ptr_bk")
    a.sta_dp(SRC + 2)
    a.stz_abs(0x4300)
    a.lda_imm(0x22)
    a.sta_abs(0x4301)
    a.lda_dp(SRC)
    a.sta_abs(0x4302)
    a.lda_dp(SRC + 1)
    a.sta_abs(0x4303)
    a.lda_dp(SRC + 2)
    a.sta_abs(0x4304)
    a.ldx_imm(0x0020)
    a.stx_abs(0x4305)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    a.rts()

    a.label("nmi")
    a.inc_dp(NMI)
    a.rti()


def place_data(rom: bytearray, bank: int, addr: int, data: bytes) -> tuple[int, int]:
    start = (bank, addr)
    for byte in data:
        rom[lorom_offset(bank, addr)] = byte
        addr += 1
        if addr > 0xFFFF:
            bank += 1
            addr = 0x8000
    return start[0], start[1], bank, addr


def align_bank(bank: int, addr: int) -> tuple[int, int]:
    if addr != 0x8000:
        return bank + 1, 0x8000
    return bank, addr


def build_pages(mapping: dict[str, int]) -> list[bytes]:
    pages: list[bytes] = []
    title_words = make_text_tilemap(
        ["", "", "", TITLE_HINT],
        mapping,
        overlays=[(13, 8, "月见桥"), (8, 12, "一封没有名字的信")],
    )
    pages.append(encode_tilemap_words(title_words))
    return pages


def compile_story(mapping: dict[str, int]) -> tuple[list[bytes], dict[str, bytes], dict[str, int]]:
    pages = build_pages(mapping)
    page_ids: dict[str, list[int]] = {}
    node_pages: dict[str, int] = {}

    for name, node in STORY.items():
        if isinstance(node, TextNode):
            words = make_text_tilemap(list(node.lines), mapping)
            node_pages[name] = len(pages)
            pages.append(encode_tilemap_words(words))
        elif isinstance(node, EndingNode):
            lines = [node.title, *node.lines[:3]]
            words = make_text_tilemap(lines, mapping)
            node_pages[name] = len(pages)
            pages.append(encode_tilemap_words(words))
        else:
            ids = []
            for sel in range(len(node.options)):
                lines = [node.prompt, *(text for text, _ in node.options)]
                words = make_text_tilemap(lines, mapping, cursor_row=1 + sel)
                ids.append(len(pages))
                pages.append(encode_tilemap_words(words))
            page_ids[name] = ids
    return pages, page_ids, node_pages


def emit_script(a: Asm, page_ids: dict[str, list[int]], node_pages: dict[str, int]) -> None:
    pending: list[tuple[int, str]] = []

    def emit_ptr(target: str) -> None:
        pending.append((a.offset(), target))
        a.emit(0, 0, 0)

    a.label("script_start")
    for name, node in STORY.items():
        a.label(f"node_{name}")
        scene = SCENE_NAMES.index(node.scene)
        a.db(OP_SCENE, scene)
        if isinstance(node, TextNode):
            a.db(OP_TEXT)
            a.dw(node_pages[name])
            a.db(OP_JUMP)
            emit_ptr(node.next)
        elif isinstance(node, ChoiceNode):
            a.db(OP_CHOICE, len(node.options))
            for i, (_text, dest) in enumerate(node.options):
                a.dw(page_ids[name][i])
                emit_ptr(dest)
        else:
            a.db(OP_END)
            a.dw(node_pages[name])

    a.resolve()
    for offset, target in pending:
        bank, addr = a.labels[f"node_{target}"]
        a.rom[offset] = addr & 0xFF
        a.rom[offset + 1] = (addr >> 8) & 0xFF
        a.rom[offset + 2] = bank & 0xFF


def build_rom() -> bytes:
    errors = story_graph_errors()
    if errors:
        raise RuntimeError("story errors: " + "; ".join(errors))

    charset = collect_charset()
    font_blob, mapping = make_font_tiles(charset)
    pages, page_ids, node_pages = compile_story(mapping)

    scenes: list[bytes] = []
    for name in SCENE_NAMES:
        tiles, tilemap, colors = image_to_tiles(paint_scene(name))
        tile_count = len(tiles) // 32
        if tile_count > 240:
            raise RuntimeError(f"scene {name} too many tiles: {tile_count}")
        tiles = tiles + bytes(SCENE_TILE_BYTES - len(tiles))
        scenes.append(tiles + tilemap + pack_palette(colors))

    rom = bytearray(ROM_SIZE)
    a = Asm(rom)
    emit_engine(a)
    if a.addr > 0xF000:
        raise RuntimeError(f"engine overflow: {a.addr:04X}")

    a.org(0x80, 0xF000)
    a.label("script_entry")
    # filled after script is placed
    a.db(0, 0, 0)
    a.labels["script_entry_hi"] = (0x80, a.labels["script_entry"][1] + 1)
    a.labels["script_entry_bk"] = (0x80, a.labels["script_entry"][1] + 2)

    a.label("font_ptr")
    a.db(0, 0, 0)
    a.labels["font_ptr_hi"] = (0x80, a.labels["font_ptr"][1] + 1)
    a.labels["font_ptr_bk"] = (0x80, a.labels["font_ptr"][1] + 2)
    a.label("font_size")
    a.dw(len(font_blob))

    a.label("textpal_ptr")
    a.db(0, 0, 0)
    a.labels["textpal_ptr_hi"] = (0x80, a.labels["textpal_ptr"][1] + 1)
    a.labels["textpal_ptr_bk"] = (0x80, a.labels["textpal_ptr"][1] + 2)

    a.label("scene_table")
    scene_table_off = a.offset()
    a.emit(*([0] * (len(SCENE_NAMES) * 3)))

    a.label("page_table")
    page_table_off = a.offset()
    a.emit(*([0] * (len(pages) * 3)))

    emit_script(a, page_ids, node_pages)
    if a.addr >= 0xFFC0:
        raise RuntimeError("bank 80 overflow into header")

    data_bank, data_addr = 0x81, 0x8000

    def put(data: bytes) -> tuple[int, int]:
        nonlocal data_bank, data_addr
        if data_addr + len(data) > 0x10000:
            data_bank, data_addr = data_bank + 1, 0x8000
        bank, addr = data_bank, data_addr
        for byte in data:
            rom[lorom_offset(data_bank, data_addr)] = byte
            data_addr += 1
            if data_addr > 0xFFFF:
                data_bank += 1
                data_addr = 0x8000
        return bank, addr

    def write_ptr(label: str, bank: int, addr: int) -> None:
        off = lorom_offset(*a.labels[label])
        rom[off] = addr & 0xFF
        rom[off + 1] = (addr >> 8) & 0xFF
        rom[off + 2] = bank & 0xFF

    def write_table(offset: int, entries: list[tuple[int, int]]) -> None:
        for i, (bank, addr) in enumerate(entries):
            rom[offset + i * 3] = addr & 0xFF
            rom[offset + i * 3 + 1] = (addr >> 8) & 0xFF
            rom[offset + i * 3 + 2] = bank & 0xFF

    fb, fa = put(font_blob)
    write_ptr("font_ptr", fb, fa)
    tb, ta = put(pack_palette(TEXT_PALETTE))
    write_ptr("textpal_ptr", tb, ta)
    write_table(scene_table_off, [put(blob) for blob in scenes])
    write_table(page_table_off, [put(page) for page in pages])

    start_bank, start_addr = a.labels[f"node_{START_NODE}"]
    write_ptr("script_entry", start_bank, start_addr)

    a.resolve()
    write_vectors(a)
    write_header(rom, "YUEJIANQIAO")
    return bytes(rom)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=ROOT / "dist" / "yuejianqiao.sfc",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rom = build_rom()
    args.output.write_bytes(rom)
    print(f"wrote {args.output} ({len(rom)} bytes)")


if __name__ == "__main__":
    main()
