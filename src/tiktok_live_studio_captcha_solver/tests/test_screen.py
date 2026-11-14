from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image
import pytest

from .. import screen


@pytest.mark.parametrize("origin", [(0, 0), (-1920, 0), (0, -1080), (-1920, -1080)])
def test_windows_capture_preserves_virtual_desktop_origin(monkeypatch, origin):
    image = Image.new("RGB", (3840, 2160))
    grab = Mock(return_value=image)
    get_metrics = Mock(side_effect=lambda index: {76: origin[0], 77: origin[1]}[index])
    monkeypatch.setattr(screen.sys, "platform", "win32")
    monkeypatch.setattr(screen.ctypes, "windll", SimpleNamespace(
        user32=SimpleNamespace(GetSystemMetrics=get_metrics)
    ), raising=False)
    monkeypatch.setattr(screen.ImageGrab, "grab", grab)

    capture = screen.capture_screen()

    grab.assert_called_once_with(all_screens=True)
    assert capture.image is image
    assert (capture.left, capture.top) == origin
    assert capture.to_desktop(250.5, 100.5) == (250.5 + origin[0], 100.5 + origin[1])


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_other_platforms_keep_existing_screenshot_backend(monkeypatch, platform):
    image = Image.new("RGB", (800, 600))
    screenshot = Mock(return_value=image)
    monkeypatch.setattr(screen.sys, "platform", platform)
    monkeypatch.setattr(screen.pyautogui, "screenshot", screenshot)
    monkeypatch.setattr(screen.ImageGrab, "grab", Mock(side_effect=AssertionError))

    capture = screen.capture_screen()

    screenshot.assert_called_once_with()
    assert capture.image is image
    assert capture.to_desktop(25, 50) == (25, 50)
