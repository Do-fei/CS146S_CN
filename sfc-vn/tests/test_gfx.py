from game.story import collect_charset
from tools.snes_gfx import make_font_tiles, make_text_tilemap


def test_font_tile_indices_fit_snes() -> None:
    blob, mapping = make_font_tiles(collect_charset())
    tile_count = len(blob) // 32
    assert tile_count <= 1024
    assert mapping["ui:bar"] < 1024


def test_fourth_text_line_stays_on_screen() -> None:
    mapping = make_font_tiles(collect_charset())[1]
    words = make_text_tilemap(["中", "秋", "前", "夜"], mapping)
    # 第四行从 tile 行 25 开始，底栏在 27
    assert (words[25 * 32 + 2] & 0x3FF) != mapping["ui:blank"]
    assert (words[26 * 32 + 2] & 0x3FF) != mapping["ui:blank"]
    assert (words[27 * 32 + 2] & 0x3FF) == mapping["ui:bar"]
