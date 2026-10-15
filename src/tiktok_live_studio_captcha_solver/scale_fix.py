import ctypes
import logging
import sys

import pyautogui

LOGGER = logging.getLogger(__name__)


def _log_screen_sizes(label):
    try:
        user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
        hdc = user32.GetDC(0)
        try:
            physical = (gdi32.GetDeviceCaps(hdc, 118), gdi32.GetDeviceCaps(hdc, 117))  # DESKTOPHORZRES, DESKTOPVERTRES
        finally:
            user32.ReleaseDC(0, hdc)
        LOGGER.info("[%s] pyautogui.size=%s screenshot.size=%s physical_screen=%s",
                    label, pyautogui.size(), pyautogui.screenshot().size, physical)
    except Exception as e:
        LOGGER.error(
            "could not log screen size due to error: " + str(e),
            exc_info=True,
            stack_info=True
        )


def scale_fix():
    if sys.platform == 'win32':
        _log_screen_sizes("before DPI fix")
        try:
            # Per-monitor DPI awareness (best for multi-monitor)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            LOGGER.info("SetProcessDpiAwareness(2) succeeded")
        except Exception as e:
            LOGGER.warning("SetProcessDpiAwareness(2) failed (%r), falling back to SetProcessDPIAware()", e)
            ctypes.windll.user32.SetProcessDPIAware()
        _log_screen_sizes("after DPI fix")
