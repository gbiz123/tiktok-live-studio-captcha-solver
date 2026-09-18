import math
import random
import time

from .exceptions import TemplateMatchNotFound
from .image_io import pil_to_b64_string
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
from .vision import draw_over_piece, extract_piece_from_puzzle, extract_puzzle_canvas, find_puzzle_captcha_box, find_shapes_captcha_box, find_slide_button_box

LOGGER = logging.getLogger(__name__)

def prompt_api_key() -> str:
    api_key = os.environ.get("SADCAPTCHA_API_KEY")
    if not api_key:
        api_key = input("Please enter your SadCaptcha API key (You can also set the SADCAPTCHA_API_KEY environment variable): ")
    return api_key

def click_proportional_point_inside_area(
    proportion_x: float,
    proportion_y: float,
    area_width: int,
    area_height: int,
    offset_x: int,
    offset_y: int
) -> None:
    """Click a proportional point within a given area on the screen. The X value where the
    click occurs is calculated as: (area_width*proportion_x)+offset_x
    The Y value where the click occurs is calculated as: (area_height*proportion_y)+offset_y """
    x_loc = (area_width * proportion_x) + offset_x
    y_loc = (area_height * proportion_y) + offset_y
    pyautogui.click(x_loc, y_loc)
    LOGGER.info(f"clicked at {x_loc}, {y_loc}")

def solve_puzzle_captcha(api_client: ApiClient) -> None:
    screenshot = pyautogui.screenshot()
    puzzle_captcha_box = find_puzzle_captcha_box(screenshot)
    LOGGER.info("puzzle captcha detected")
    cropped_screenshot = screenshot.crop(
        (
            puzzle_captcha_box.left,
            puzzle_captcha_box.top,
            puzzle_captcha_box.width + puzzle_captcha_box.left,
            puzzle_captcha_box.top + puzzle_captcha_box.height
        )
    )
    cropped_screenshot.save("cropped.png")
    puzzle_canvas = extract_puzzle_canvas(cropped_screenshot)
    piece = extract_piece_from_puzzle(puzzle_canvas)
    puzzle_modified = draw_over_piece(puzzle_canvas)
    piece_b64 = pil_to_b64_string(piece)
    puzzle_b64 = pil_to_b64_string(puzzle_modified)
    resp = api_client.puzzle(puzzle_b64, piece_b64)
    LOGGER.info("got response for puzzle captcha: " + resp.__repr__())

    # Determine distance needed to drag slider
    distance = int(resp.slide_x_proportion * puzzle_canvas.width)
    button = find_slide_button_box(screenshot)
    start_x = button.left + (button.width / 2)
    start_y = button.top  + (button.height / 2)
    end_x = start_x + distance
    pyautogui.moveTo(start_x, start_y)
    time.sleep(0.2)
    pyautogui.mouseDown(start_x, start_y)
    time.sleep(0.5)
    overshoot = 15
    for i in range(0, distance + overshoot, 5):
        if random.random() > 0.35:
            x_adjust = random.randint(0, 4)
            y_adjust = (random.random() - 1) * 2
            pyautogui.moveTo(start_x + i + x_adjust, start_y + y_adjust)
    for i in range(0, overshoot, 3):
        pyautogui.moveTo(end_x + overshoot - i, start_y)
    pyautogui.mouseUp(end_x, start_y)
    LOGGER.info("solved puzzle captcha")
    time.sleep(5)


def solve_shapes_captcha(api_client: ApiClient) -> None:
    screenshot = pyautogui.screenshot()
    shapes_captcha_box = find_shapes_captcha_box(screenshot)
    LOGGER.info("shapes captcha detected")
    cropped_screenshot = screenshot.crop(
        (
            shapes_captcha_box.left,
            shapes_captcha_box.top,
            shapes_captcha_box.width + shapes_captcha_box.left,
            shapes_captcha_box.top + shapes_captcha_box.height
        )
    )
    img_b64 = pil_to_b64_string(cropped_screenshot)
    resp = api_client.shapes(img_b64)
    LOGGER.info("got response for shapes captcha: " + resp.__repr__())
    # Click first point, and then second point
    click_proportional_point_inside_area(
        resp.point_one_proportion_x,
        resp.point_one_proportion_y,
        shapes_captcha_box.width,
        shapes_captcha_box.height,
        shapes_captcha_box.left,
        shapes_captcha_box.top
    )
    LOGGER.info("clicked first shape")
    time.sleep(0.5)
    click_proportional_point_inside_area(
        resp.point_two_proportion_x,
        resp.point_two_proportion_y,
        shapes_captcha_box.width,
        shapes_captcha_box.height,
        shapes_captcha_box.left,
        shapes_captcha_box.top
    )
    LOGGER.info("clicked second shape")
    # Click confirm button
    time.sleep(0.5)
    pyautogui.click(
        shapes_captcha_box.left + (shapes_captcha_box.width / 2),
        shapes_captcha_box.top + (shapes_captcha_box.height - 15)
    )
    LOGGER.info("clicked confirm button")
    time.sleep(5)

def solve_loop(api_client: ApiClient):
    while True:
        for captcha_type in CaptchaType:
            try:
                match(captcha_type):
                    case CaptchaType.SHAPES:
                        solve_shapes_captcha(api_client)
                    case CaptchaType.PUZZLE:
                        solve_puzzle_captcha(api_client)
            except TemplateMatchNotFound as e:
                LOGGER.debug(f"{captcha_type} captcha not found")
            except Exception as e:
                LOGGER.error(
                    "unexpected exception occurred during solve loop: " + str(e),
                    exc_info=True,
                    stack_info=True
                )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api_key = prompt_api_key()
    api_client = ApiClient(api_key)
    solve_loop(api_client)
