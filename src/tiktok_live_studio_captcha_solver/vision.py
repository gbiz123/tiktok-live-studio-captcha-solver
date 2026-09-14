import logging
from PIL import Image

import cv2
from pyscreeze import Box
import numpy as np

LOGGER = logging.getLogger(__name__)
SHAPES_CAPTCHA_SAMPLE_PATH = "./src/tiktok_live_studio_captcha_solver/resources/shapes_captcha_sample.png"

def scale_invariant_template_match(
    mat: cv2.typing.MatLike,
    template: cv2.typing.MatLike,
    scale_factor: float = 0.2,
    scale_step: float = 0.01
) -> cv2.Mat:
    start = 1.0 - scale_factor
    end = 1.0 + scale_factor
    for scale in range(start, end, scale_step):
        width = template.w
        resized = cv2.resize(template, )
        mat = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        res = cv2.matchTemplate(mat, SHAPES_CAPTCHA_SAMPLE, cv2.TM_CCOEFF_NORMED)


def find_shapes_captcha_box(image: Image.Image) -> Box:
    """Find the area of the shapes captcha image as PIL image as a pyscreeze box"""
    SHAPES_CAPTCHA_SAMPLE = cv2.imread(
        SHAPES_CAPTCHA_SAMPLE_PATH,
        cv2.IMREAD_GRAYSCALE
    )

    if SHAPES_CAPTCHA_SAMPLE is None:
        raise ValueError("Could not load shapes captcha sample image at " + SHAPES_CAPTCHA_SAMPLE_PATH)

    res = scale_invariant_template_match(mat, SHAPES_CAPTCHA_SAMPLE)

    w, h = SHAPES_CAPTCHA_SAMPLE.shape[::-1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat ,top_left, bottom_right, 255, 2)
    cv2.imwrite("./images/test_shapes_captcha_match.png", mat)
