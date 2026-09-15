from tiktok_live_studio_captcha_solver.exceptions import TemplateMatchNotFound
from tiktok_live_studio_captcha_solver.image_io import pil_to_b64_string
from .system import tkinter_is_installed

if __name__ == "__main__":
    if not tkinter_is_installed():
        print("tkinter is not installed on the system. To run this program, you must install tkinter.")
        exit(1)

import dataclasses
import logging
import os
import pyautogui
from pyscreeze import Box

from .captchatype import CaptchaType
from .api import ApiClient
from .vision import find_shapes_captcha_box

LOGGER = logging.getLogger(__name__)

def prompt_api_key() -> str:
    api_key = os.environ.get("SADCAPTCHA_API_KEY")
    if not api_key:
        api_key = input("Please enter your SadCaptcha API key (You can also set the SADCAPTCHA_API_KEY environment variable): ")
    return api_key

def solve_shapes_captcha(api_client: ApiClient) -> None:
    screenshot = pyautogui.screenshot()
    shapes_captcha_box = find_shapes_captcha_box(screenshot)
    cropped = screenshot.crop(
        (
            shapes_captcha_box.left,
            shapes_captcha_box.top,
            shapes_captcha_box.width + shapes_captcha_box.left,
            shapes_captcha_box.top + shapes_captcha_box.height
        )
    )
    cropped.save("./images/extracted.png")
    img_b64 = pil_to_b64_string(cropped)
    resp = api_client.shapes(img_b64)
    LOGGER.debug("got response for shapes captcha: " + resp.__repr__())

def solve_loop(api_client: ApiClient):
    while True:
        for captcha_type in CaptchaType:
            try:
                match(captcha_type):
                    case CaptchaType.SHAPES:
                        solve_shapes_captcha(api_client)
            except TemplateMatchNotFound as e:
                LOGGER.debug(f"{captcha_type} captcha not found")
            except Exception as e:
                LOGGER.error(
                    "unexpected exception occurred during solve loop: " + str(e),
                    exc_info=True,
                    stack_info=True
                )

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    api_key = prompt_api_key()
    api_client = ApiClient(api_key)
    solve_loop(api_client)
