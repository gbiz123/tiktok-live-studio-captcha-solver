import ctypes
import logging
import sys


LOGGER = logging.getLogger(__name__)

def scale_fix():
    if sys.platform == 'win32':
        try:
            # Per-monitor DPI awareness (best for multi-monitor)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            LOGGER.info("SetProcessDpiAwareness(2) succeeded")
        except Exception as e:
            LOGGER.warning("SetProcessDpiAwareness(2) failed (%r), falling back to SetProcessDPIAware()", e)
            ctypes.windll.user32.SetProcessDPIAware()
