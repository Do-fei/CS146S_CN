from game.nodes import EndingNode, estimate_minutes
from game.story import SCENE_TITLES, START_NODE, STORY, collect_charset, screen_count, story_graph_errors
from tools.art import all_scene_names


def test_story_graph_is_complete() -> None:
    assert story_graph_errors() == []
    assert START_NODE in STORY


def test_three_routes_and_nine_endings() -> None:
    endings = {name for name, node in STORY.items() if isinstance(node, EndingNode)}
    assert len(endings) == 9
    assert any(name.startswith("end_tape") for name in endings)
    assert any(name.startswith("end_aqua") for name in endings)
    assert any(name.startswith("end_rail") for name in endings)


def test_story_scenes_have_art() -> None:
    names = set(all_scene_names())
    for node in STORY.values():
        assert node.scene in names
        assert node.scene in SCENE_TITLES


def test_long_enough_for_one_hour() -> None:
    assert screen_count(16, 4) >= 200
    assert estimate_minutes(STORY) >= 30
    assert len(collect_charset()) > 200
