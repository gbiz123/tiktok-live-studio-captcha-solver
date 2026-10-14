import os
import logging
from PIL import Image, ImageDraw
import pyautogui
import pyscreeze

import cv2
from pyscreeze import Box, screenshot
import numpy as np

from tiktok_live_studio_captcha_solver.captchatype import CaptchaType
from tiktok_live_studio_captcha_solver.logs import log_image

from .exceptions import TemplateMatchNotFound

def binary_thresh(mat: cv2.typing.MatLike) -> cv2.typing.MatLike:
    _, thresh = cv2.threshold(mat, 10, 255, cv2.THRESH_BINARY, dst=mat)
    LOGGER.debug("applied binary thresholding")
    return thresh

def sobel(img: cv2.typing.MatLike) -> cv2.typing.MatLike:
    sobelx = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=3)
    sobely = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=3)
    sobel_combined = cv2.magnitude(sobelx, sobely)
    sobel_8bit = np.uint8(np.absolute(sobel_combined))
    return sobel_8bit

LOGGER = logging.getLogger(__name__)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_PATHS = {
    "shapes": {
        "img_path": os.path.join(MODULE_DIR, "resources/shapes_template.png"),
        "mask_path": os.path.join(MODULE_DIR, "resources/shapes_template_mask.png"),
    },
    "puzzle_canvas": {
        "img_path": os.path.join(MODULE_DIR, "resources/puzzle_canvas_template.png"),
        "mask_path":  os.path.join(MODULE_DIR, "resources/puzzle_canvas_template_mask.png"),
    },
    "puzzle_canvas_large": {
        "img_path": os.path.join(MODULE_DIR, "resources/puzzle_canvas_template_large.png"),
        "mask_path":  os.path.join(MODULE_DIR, "resources/puzzle_canvas_template_mask_large.png"),
    },
    "puzzle": {
        "img_path": os.path.join(MODULE_DIR, "resources/puzzle_template.png"),
        "mask_path": os.path.join(MODULE_DIR, "resources/puzzle_template_mask.png"),
    },
    "puzzle_large": {
        "img_path": os.path.join(MODULE_DIR, "resources/puzzle_template_large.png"),
        "mask_path": os.path.join(MODULE_DIR, "resources/puzzle_template_mask_large.png"),
    },
    "slide_button": {
        "img_path":  os.path.join(MODULE_DIR, "resources/slide_button_template.png"),
        "mask_path": os.path.join(MODULE_DIR, "resources/slide_button_template_mask.png")
    }
}

IMAGES: dict[str, dict[str, cv2.typing.MatLike]] = {}

for k, v in IMAGE_PATHS.items():
    img = cv2.imread(v["img_path"], cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("no image found at path: " + v["img_path"])
    mask = cv2.imread(v["mask_path"], cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError("no mask found at path: " + v["mask_path"])
    IMAGES[k] = {
        "image": sobel(img),
        "mask": mask
    }

for name, entry in IMAGES.items():
    log_image(Image.fromarray(entry["mask"]), f"{name}-template-mask.png")
    log_image(Image.fromarray(entry["image"]), f"{name}-template.png")


def scale_invariant_template_match(
    mat: cv2.typing.MatLike,
    template: cv2.typing.MatLike,
    scale_factor_shrink: float = 0.1,
    scale_factor_grow: float = 0.3,
    scale_step: float = 0.020,
    mask: cv2.typing.MatLike | None = None,
    threshold: float | None = None
) -> tuple[cv2.typing.MatLike, float]:
    """Perform scale invariant template matching returning (mat, scale) tuple"""
    start = 1.0
    end = 1.0 + scale_factor_grow
    best_val = -1
    best_res = None
    best_scale = -1
    for scale in np.arange(start, end, scale_step):
        height, width = template.shape[0:2]
        resized_template = cv2.resize(template, (int(width*scale), int(height*scale)))
        if mask is not None:
            resized_mask = cv2.resize(mask, (int(width*scale), int(height*scale)))
        else:
            resized_mask = None
        try:
            res = cv2.matchTemplate(
                mat,
                resized_template,
                cv2.TM_CCORR_NORMED,
                mask=resized_mask
            )
            res[np.isinf(res)] = 0.0
            res[np.isnan(res)] = 0.0
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_res = res
                best_scale = scale
        except cv2.error as e:
            LOGGER.debug(f"failed template match at scale {scale} due to opencv error - {str(e)}")
    if best_res is None:
        raise ValueError("Could not find best result for scale invariant template match - best_res was None")
    if threshold is not None \
            and best_val < threshold:
        msg = f"Could not find template on image (confidence was {best_val}, threshold {threshold})"
        LOGGER.debug(msg)
        raise TemplateMatchNotFound(msg)
    LOGGER.debug("found best matching location for template, with confidence " + str(best_val) + " and scale " + str(best_scale))
    return best_res, best_scale


def find_shapes_captcha_box(
    screenshot: Image.Image
) -> Box:
    """Find the area of the shapes captcha image as PIL image as a pyscreeze box"""

    template = IMAGES["shapes"]["image"]
    mask = IMAGES["shapes"]["mask"]

    mat = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    mat = sobel(mat)
    log_image(Image.fromarray(mat), "screenshot-processed.png")

    res, scale = scale_invariant_template_match(
        mat,
        template,
        mask=mask,
        threshold=0.60
    )

    w, h = template.shape[::-1]
    w = int(w * scale)
    h = int(h * scale)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat, top_left, bottom_right, 255, 2)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h)
    LOGGER.debug("found shapes captcha box at " + box.__repr__())
    return box


def find_puzzle_captcha_box(
    screenshot: Image.Image
) -> Box:
    """Find the area of the puzzle captcha image as PIL image as a pyscreeze box"""

    template = IMAGES["puzzle"]["image"]
    mask = IMAGES["puzzle"]["mask"]

    mat = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    mat = sobel(mat)
    log_image(Image.fromarray(mat), "screenshot-processed.png")

    res, scale = scale_invariant_template_match(
        mat,
        template,
        mask=mask,
        threshold=0.6
    )

    w, h = template.shape[::-1]
    w = int(w * scale)
    h = int(h * scale)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat, top_left, bottom_right, 255, 2)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h)
    LOGGER.debug("found puzzle captcha box at " + box.__repr__())
    return box


def find_slide_button_box(
    screenshot: Image.Image
) -> Box:
    """Find the area of the slide arrow button image as PIL image as a pyscreeze box"""

    template = IMAGES["slide_button"]["image"]
    mask = IMAGES["slide_button"]["mask"]

    mat = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    mat = sobel(mat)
    log_image(Image.fromarray(mat), "screenshot-sobel.png")

    res, scale = scale_invariant_template_match(
        mat,
        template,
        mask=mask,
        threshold=None
    )

    w, h = template.shape[::-1]
    w = int(w * scale)
    h = int(h * scale)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    _ = cv2.rectangle(mat, top_left, bottom_right, 255, 2)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h)
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
    template = IMAGES["puzzle_canvas"]["image"]
    mask = IMAGES["puzzle_canvas"]["mask"]

    mat = np.array(screenshot)
    mat_sobel = cv2.cvtColor(sobel(mat), cv2.COLOR_RGB2GRAY)

    res, scale = scale_invariant_template_match(
        mat_sobel,
        template,
        mask=mask,
        threshold=None
    )

    w, h = template.shape[::-1]
    w = int(w * scale)
    h = int(h * scale)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    submat = mat[
        max_loc[1]:max_loc[1] + h,
        max_loc[0]:max_loc[0] + w
    ].copy()
    pil_image = Image.fromarray(submat)
    LOGGER.debug("extracted puzzle canvas from image")
    return pil_image


def extract_piece_from_puzzle(
    puzzle_image: Image.Image
) -> Image.Image:
    cropped = puzzle_image.crop(
        (
            0,
            0,
            puzzle_image.width * 0.25,
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


def identify_captcha(
    screenshot: Image.Image,
    threshold: float = 0.60
) -> CaptchaType | None:
    processed_screenshot = sobel(cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY))

    puzzle_res, _ = scale_invariant_template_match(
        processed_screenshot,
        IMAGES["puzzle"]["image"],
        mask=IMAGES["puzzle"]["mask"],
        threshold=None
    )
    _, max_puzzle, _, _ = cv2.minMaxLoc(puzzle_res)

    shapes_res, _ = scale_invariant_template_match(
        processed_screenshot,
        IMAGES["shapes"]["image"],
        mask=IMAGES["shapes"]["mask"],
        threshold=None
    )
    _, max_shapes, _, _ = cv2.minMaxLoc(shapes_res)

    if not any(
        [
            max_shapes > threshold,
            max_puzzle > threshold
        ]
    ):
        LOGGER.debug("no captcha found")
    elif max_shapes > max_puzzle:
        LOGGER.debug("shapes captcha found")
        return CaptchaType.SHAPES
    else:
        LOGGER.debug("puzzle captcha found")
        return CaptchaType.PUZZLE
