import os
import logging
from PIL import Image, ImageDraw
import pyautogui
import pyscreeze

import cv2
from pyscreeze import Box, screenshot
import numpy as np

from .exceptions import TemplateMatchNotFound

def sobel(img: cv2.typing.MatLike) -> cv2.typing.MatLike:
    sobelx = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=3)
    sobely = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=3)
    sobel_combined = cv2.magnitude(sobelx, sobely)
    sobel_8bit = np.uint8(np.absolute(sobel_combined))
    return sobel_8bit

LOGGER = logging.getLogger(__name__)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
SHAPES_TEMPLATE_PATH = os.path.join(MODULE_DIR, "resources/shapes_template.png")
SHAPES_TEMPLATE_MASK_PATH = os.path.join(MODULE_DIR, "resources/shapes_template_mask.png")
PUZZLE_CANVAS_TEMPLATE_PATH = os.path.join(MODULE_DIR, "resources/puzzle_canvas_template.png")
PUZZLE_CANVAS_TEMPLATE_MASK_PATH = os.path.join(MODULE_DIR, "resources/puzzle_canvas_template_mask.png")
PUZZLE_TEMPLATE_PATH = os.path.join(MODULE_DIR, "resources/puzzle_template.png")
PUZZLE_TEMPLATE_MASK_PATH = os.path.join(MODULE_DIR, "resources/puzzle_template_mask.png")
SLIDE_BUTTON_TEMPLATE_PATH = os.path.join(MODULE_DIR, "resources/slide_button_template.png")

# Load slide button template
SLIDE_BUTTON_TEMPLATE_BASE = cv2.imread(
    SLIDE_BUTTON_TEMPLATE_PATH,
    cv2.IMREAD_GRAYSCALE
)
if SLIDE_BUTTON_TEMPLATE_BASE is None:
    raise ValueError("Could not load slide button template sample image at " + SLIDE_BUTTON_TEMPLATE_PATH)
SLIDE_BUTTON_TEMPLATE = sobel(SLIDE_BUTTON_TEMPLATE_BASE)

# Load puzzle canvas template
PUZZLE_CANVAS_TEMPLATE_BASE = cv2.imread(
    PUZZLE_CANVAS_TEMPLATE_PATH,
    cv2.IMREAD_GRAYSCALE
)
if PUZZLE_CANVAS_TEMPLATE_BASE is None:
    raise ValueError("Could not load puzzle canvas captcha sample image at " + PUZZLE_CANVAS_TEMPLATE_PATH)
PUZZLE_CANVAS_TEMPLATE = sobel(PUZZLE_CANVAS_TEMPLATE_BASE)

# Load puzzle canvas template mask
PUZZLE_CANVAS_TEMPLATE_MASK = cv2.imread(
    PUZZLE_CANVAS_TEMPLATE_MASK_PATH,
    cv2.IMREAD_GRAYSCALE
)
if PUZZLE_CANVAS_TEMPLATE_MASK is None:
    raise ValueError("Could not load puzzle canvas captcha template mask at " + PUZZLE_CANVAS_TEMPLATE_PATH)

# Load puzzle template
PUZZLE_TEMPLATE_BASE = cv2.imread(
    PUZZLE_TEMPLATE_PATH,
    cv2.IMREAD_GRAYSCALE
)
if PUZZLE_TEMPLATE_BASE is None:
    raise ValueError("Could not load puzzle captcha sample image at " + PUZZLE_TEMPLATE_PATH)
PUZZLE_TEMPLATE = sobel(PUZZLE_TEMPLATE_BASE)

# Load puzzle template mask
PUZZLE_TEMPLATE_MASK = cv2.imread(
    PUZZLE_TEMPLATE_MASK_PATH,
    cv2.IMREAD_GRAYSCALE
)
if PUZZLE_TEMPLATE_MASK is None:
    raise ValueError("Could not load puzzle captcha template mask at " + PUZZLE_TEMPLATE_PATH)

# Load shapes template
SHAPES_TEMPLATE_BASE = cv2.imread(
    SHAPES_TEMPLATE_PATH,
    cv2.IMREAD_GRAYSCALE
)
if SHAPES_TEMPLATE_BASE is None:
    raise ValueError("Could not load shapes captcha sample image at " + SHAPES_TEMPLATE_PATH)
SHAPES_TEMPLATE = sobel(SHAPES_TEMPLATE_BASE)

# Load shapes template mask
SHAPES_TEMPLATE_MASK = cv2.imread(
    SHAPES_TEMPLATE_MASK_PATH,
    cv2.IMREAD_GRAYSCALE
)
if SHAPES_TEMPLATE_MASK is None:
    raise ValueError("Could not load shapes captcha template mask at " + SHAPES_TEMPLATE_PATH)

def scale_invariant_template_match(
    mat: cv2.typing.MatLike,
    template: cv2.typing.MatLike,
    scale_factor: float = 0.1,
    scale_step: float = 0.01,
    mask: cv2.typing.MatLike | None = None,
    threshold: float | None = None
) -> cv2.typing.MatLike:
    start = 1.0 - scale_factor
    end = 1.0 + scale_factor
    best_val = -1
    best_res = None
    for scale in np.arange(start, end, scale_step):
        height, width = template.shape[0:2]
        resized_template = cv2.resize(template, (int(width*scale), int(height*scale)))
        if mask is not None:
            mask = cv2.resize(mask, (int(width*scale), int(height*scale)))
        res = cv2.matchTemplate(
            mat,
            resized_template,
            cv2.TM_CCORR_NORMED,
            mask=mask
        )
        # Replace positive and negative infinities with safe boundary values (0.0)
        res[np.isinf(res)] = 0.0
        res[np.isnan(res)] = 0.0
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val = max_val
            best_res = res
    if best_res is None:
        raise ValueError("Could not find best result for scale invariant template match")
    if threshold is not None \
            and best_val < threshold:
        raise TemplateMatchNotFound(f"Could not find template on image (confidence was {best_val}, threshold {threshold})")
    LOGGER.debug("found best matching location for shapes template, with confidence " + str(best_val))
    return best_res


def find_shapes_captcha_box(
    screenshot: Image.Image
) -> Box:
    """Find the area of the shapes captcha image as PIL image as a pyscreeze box"""

    mat = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    mat = sobel(mat)

    res = scale_invariant_template_match(
        mat,
        SHAPES_TEMPLATE,
        mask=SHAPES_TEMPLATE_MASK,
        threshold=0.9
    )

    w, h = SHAPES_TEMPLATE.shape[::-1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat ,top_left, bottom_right, 255, 2)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h )
    LOGGER.debug("found shapes captcha box at " + box.__repr__())
    return box

def find_puzzle_captcha_box(
    screenshot: Image.Image
) -> Box:
    """Find the area of the puzzle captcha image as PIL image as a pyscreeze box"""

    mat = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    mat = sobel(mat)

    res = scale_invariant_template_match(
        mat,
        PUZZLE_TEMPLATE,
        mask=PUZZLE_TEMPLATE_MASK,
        threshold=0.9
    )

    w, h = PUZZLE_TEMPLATE.shape[::-1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat ,top_left, bottom_right, 255, 2)
    # cv2.imwrite("images/test_extracted_captcha_box.png", mat)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h )
    LOGGER.debug("found puzzle captcha box at " + box.__repr__())
    return box

def find_slide_button_box(
    screenshot: Image.Image
) -> Box:
    """Find the area of the slide arrow button image as PIL image as a pyscreeze box"""

    mat = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    mat = sobel(mat)

    res = scale_invariant_template_match(
        mat,
        SLIDE_BUTTON_TEMPLATE,
        threshold=0.9
    )

    w, h = SLIDE_BUTTON_TEMPLATE.shape[::-1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat ,top_left, bottom_right, 255, 2)
    # cv2.imwrite("images/test_extracted_slide_button.png", mat)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h )
    LOGGER.debug("found slide button box at " + box.__repr__())
    return box

def extract_puzzle_canvas(
    screenshot: Image.Image,
) -> Image.Image:
    """Extract the puzzle canvas image itself from within the 
    puzzle captcha box.

    args:
        screenshot: PIL image of the entire screen
        puzzle_captcha_box: Box containing the bounds of the entire puzzle captcha (extracted with find_puzzle_captcha_box)
    """
    mat = np.array(screenshot)
    mat_sobel = cv2.cvtColor(sobel(mat), cv2.COLOR_RGB2GRAY)

    res = scale_invariant_template_match(
        mat_sobel,
        PUZZLE_CANVAS_TEMPLATE,
        mask=PUZZLE_CANVAS_TEMPLATE_MASK,
        threshold=0.9
    )

    w, h = PUZZLE_CANVAS_TEMPLATE.shape[::-1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    submat = mat[
        max_loc[1]:max_loc[1] + h,
        max_loc[0]:max_loc[0] + w
    ].copy()
    top_left = max_loc
    pil_image = Image.fromarray(submat)
    LOGGER.debug("extracted puzzle canvas from image")
    return pil_image

def extract_piece_from_puzzle(
    puzzle_image: Image.Image
) -> Image.Image:
    cropped = puzzle_image.crop(
        (
            10,
            10,
            puzzle_image.width * 0.2,
            puzzle_image.height - 10
        )
    )
    LOGGER.debug("cropped PIL image")
    return cropped

def draw_over_piece(
    puzzle_image: Image.Image
) -> Image.Image:
    puzzle_copy = puzzle_image.copy()
    draw = ImageDraw.Draw(puzzle_copy)
    draw.ellipse(
        (
            0,
            0,
            puzzle_copy.width * 0.25,
            puzzle_copy.height 
        ),
        fill="black",
        outline="black",
        width=1
    )
    LOGGER.debug("drew rectangle over piece")
    return puzzle_copy
