import dataclasses
import logging
import os
import pyautogui
from pyscreeze import Box, Point

CONFIRM_BUTTON_PATH = "./src/tiktok_live_studio_captcha_solver/resources/confirm.png"

LOGGER = logging.getLogger(__name__)

@dataclasses.dataclass
class ImageB64WithBox:
    image_b64: str
    box: Box

def prompt_api_key() -> str:
    api_key = os.environ.get("SADCAPTCHA_API_KEY")
    if not api_key:
        api_key = input("Please enter your SadCaptcha API key (You can also set the SADCAPTCHA_API_KEY environment variable): ")
    return api_key

def locate_image_on_screen(image_path: str) -> Box | None:
    try:
        box = pyautogui.locateOnScreen(CONFIRM_BUTTON_PATH)
        LOGGER.debug(f"found image {image_path} on screen at {box.__repr__()}")
        return box
    except pyautogui.ImageNotFoundException as e:
        LOGGER.debug(f"image {image_path} not found on screen")
        return None

def get_captcha_background_as_b64() -> ImageB64WithBox:
    # Take screenshot of entire screen
    # Template match the region that looks like the sample shapes captcha template
    # Extract this region as b64 image, return as ImageB64WithBox
    # Throws an error if it cant find the image


def solve_loop():
    pass

if __name__ == "__main__":
    api_key = prompt_api_key()
    solve_loop()
