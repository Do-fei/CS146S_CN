from game.story import MAX_GLYPHS, STORY, START_NODE, EndingNode, collect_charset, story_graph_errors


def test_story_graph_is_complete() -> None:
    assert story_graph_errors() == []
    assert START_NODE in STORY


def test_charset_fits_snes_tile_limit() -> None:
    assert len(collect_charset()) <= MAX_GLYPHS


def test_three_endings_exist() -> None:
    endings = [name for name, node in STORY.items() if isinstance(node, EndingNode)]
    assert set(endings) == {"end_home", "end_far", "end_wait"}
