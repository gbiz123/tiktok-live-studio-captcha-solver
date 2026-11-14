from types import SimpleNamespace
from unittest.mock import Mock, call

from PIL import Image
from pyscreeze import Box
import pytest

from .. import solver
from ..captchatype import CaptchaType
from ..screen import ScreenCapture


@pytest.fixture
def mouse(monkeypatch):
    """Never send real mouse input, wait, or call a remote API in these tests."""
    mouse = Mock()
    monkeypatch.setattr(solver, "pyautogui", mouse)
    monkeypatch.setattr(solver.time, "sleep", Mock())
    monkeypatch.setattr(solver, "log_image", Mock())
    monkeypatch.setattr(solver, "capture_screen", Mock(side_effect=AssertionError))
    return mouse


# Include a primary monitor, secondary monitors to the right/below, and negative
# coordinates for monitors to the left/above the primary display.
LAYOUTS = [
    (0, 0, 0, 0),
    (0, 0, 1920, 0),
    (0, 0, 0, 1080),
    (-1920, 0, 0, 0),
    (0, -1080, 0, 0),
    (-1920, -1080, 0, 0),
    (-1920, 0, 1920, 0),
]


@pytest.mark.parametrize("left,top,image_x,image_y", LAYOUTS)
def test_puzzle_drag_uses_desktop_coordinates(monkeypatch, mouse, left, top, image_x, image_y):
    capture = ScreenCapture(Image.new("RGB", (3840, 2160), "white"), left, top)
    box = Box(image_x + 100, image_y + 100, 400, 300)
    button = Box(image_x + 120, image_y + 350, 40, 40)
    monkeypatch.setattr(solver, "find_puzzle_captcha_box", Mock(return_value=box))
    monkeypatch.setattr(solver, "find_slide_button_box", Mock(return_value=button))
    canvas = Image.new("RGB", (300, 150))
    extract = Mock(return_value=canvas)
    monkeypatch.setattr(solver, "extract_puzzle_canvas", extract)
    api = Mock()
    api.puzzle.return_value = SimpleNamespace(slide_x_proportion=0.5)

    solver.solve_puzzle_captcha(api, capture)

    # Crops remain image-relative even when mouse coordinates are negative.
    assert extract.call_args.args[0].size == (400, 300)
    start = (left + image_x + 140, top + image_y + 370)
    end = (start[0] + 150, start[1])
    mouse.mouseDown.assert_called_once_with(*start)
    mouse.mouseUp.assert_called_once_with(*end)
    assert mouse.moveTo.call_args_list[0] == call(*start)
    assert mouse.moveTo.call_args_list[1].args == (end[0] + 15, end[1] + 7)
    assert mouse.moveTo.call_args_list[2].args == end
    api.puzzle.assert_called_once()


@pytest.mark.parametrize("left,top,image_x,image_y", LAYOUTS)
def test_shapes_and_confirm_clicks_use_desktop_coordinates(monkeypatch, mouse, left, top, image_x, image_y):
    capture = ScreenCapture(Image.new("RGB", (3840, 2160), "white"), left, top)
    box = Box(image_x + 100, image_y + 100, 400, 300)
    monkeypatch.setattr(solver, "find_shapes_captcha_box", Mock(return_value=box))
    api = Mock()
    api.shapes.return_value = SimpleNamespace(
        point_one_proportion_x=0.25, point_one_proportion_y=0.25,
        point_two_proportion_x=0.75, point_two_proportion_y=0.75,
    )

    solver.solve_shapes_captcha(api, capture)

    x = left + image_x
    y = top + image_y
    assert mouse.click.call_args_list == [
        call(x + 200, y + 175),
        call(x + 400, y + 325),
        call(x + 300, y + 385),
    ]
    api.shapes.assert_called_once()


@pytest.mark.parametrize("kind,handler", [
    (CaptchaType.PUZZLE, "solve_puzzle_captcha"),
    (CaptchaType.SHAPES, "solve_shapes_captcha"),
])
def test_loop_passes_the_detected_capture_to_handler(monkeypatch, mouse, kind, handler):
    capture = ScreenCapture(Image.new("RGB", (100, 100)), -1920, -1080)
    capture_screen = Mock(side_effect=[capture, KeyboardInterrupt()])
    monkeypatch.setattr(solver, "capture_screen", capture_screen)
    identify = Mock(return_value=kind)
    monkeypatch.setattr(solver, "identify_captcha", identify)
    solve = Mock()
    monkeypatch.setattr(solver, handler, solve)
    api = Mock()

    with pytest.raises(KeyboardInterrupt):
        solver.solve_loop(api)

    identify.assert_called_once_with(capture.image)
    solve.assert_called_once_with(api, capture)
