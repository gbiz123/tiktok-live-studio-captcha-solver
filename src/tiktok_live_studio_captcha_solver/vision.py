from PIL import Image

import cv2
from pyscreeze import Box
import numpy as np


SHAPES_CAPTCHA_SAMPLE_PATH = "./src/tiktok_live_studio_captcha_solver/resources/shapes_captcha_sample.png"

def find_shapes_captcha_box(image: Image.Image) -> Box:
    """Find the area of the shapes captcha image as PIL image as a pyscreeze box"""
    SHAPES_CAPTCHA_SAMPLE = cv2.imread(
        SHAPES_CAPTCHA_SAMPLE_PATH,
        cv2.IMREAD_GRAYSCALE
    )

    if not SHAPES_CAPTCHA_SAMPLE:
        raise ValueError("Could not load shapes captcha sample image at " + SHAPES_CAPTCHA_SAMPLE_PATH)

    mat = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    res = cv2.matchTemplate(mat, SHAPES_CAPTCHA_SAMPLE, cv2.TM_CCOEFF_NORMED)
