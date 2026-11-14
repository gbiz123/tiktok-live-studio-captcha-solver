"""Capture screenshots together with their desktop-coordinate origin."""

import ctypes
from dataclasses import dataclass
import sys

from PIL import Image, ImageGrab
import pyautogui


@dataclass(frozen=True)
class ScreenCapture:
    image: Image.Image
    left: int = 0
    top: int = 0

    def to_desktop(self, x: float, y: float) -> tuple[float, float]:
        """Convert an image-relative point to a desktop mouse position."""
        return x + self.left, y + self.top


def capture_screen() -> ScreenCapture:
    if sys.platform == "win32":
        # Pillow's image starts at the virtual desktop's top-left corner,
        # which is not necessarily (0, 0). Keep that origin with the image.
        user32 = ctypes.windll.user32
        left = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        top = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        return ScreenCapture(ImageGrab.grab(all_screens=True), left, top)

    # Preserve the existing screenshot backend on other platforms.
    return ScreenCapture(pyautogui.screenshot())
