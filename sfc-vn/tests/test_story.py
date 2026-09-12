from game.nodes import EndingNode, estimate_minutes
from game.story import START_NODE, STORY, collect_charset, screen_count, story_graph_errors


def test_story_graph_is_complete() -> None:
    assert story_graph_errors() == []
    assert START_NODE in STORY


def test_three_routes_and_nine_endings() -> None:
    endings = {name for name, node in STORY.items() if isinstance(node, EndingNode)}
    assert len(endings) == 9
    assert any(name.startswith("end_tape") for name in endings)
    assert any(name.startswith("end_aqua") for name in endings)
    assert any(name.startswith("end_rail") for name in endings)


def test_long_enough_for_one_hour() -> None:
    assert screen_count(16, 4) >= 200
    assert estimate_minutes(STORY) >= 30
    assert len(collect_charset()) > 200
