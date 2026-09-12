from tools.art import WEB_SCENE, all_scene_names, paint_portrait, paint_scene, paint_scene_web


def test_scenes_are_snes_resolution() -> None:
    for name in all_scene_names():
        im = paint_scene(name)
        assert im.size == (256, 224)


def test_web_scenes_are_three_by_two() -> None:
    assert WEB_SCENE == (960, 640)
    im = paint_scene_web("title")
    assert im.size == (960, 640)


def test_portraits_exist() -> None:
    for name in ("linxia", "qing", "zhou", "hai", "clerk"):
        im = paint_portrait(name)
        assert im.size == (72, 96)
        assert im.mode == "RGBA"
        assert im.getextrema()[0][1] > 20
        assert im.getextrema()[3][0] == 0
