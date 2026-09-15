import logging
from PIL import Image

import cv2
from pyscreeze import Box
import numpy as np

from .exceptions import TemplateMatchNotFound

def sobel(img: cv2.typing.MatLike) -> cv2.typing.MatLike:
    sobelx = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=3)
    sobely = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=3)
    sobel_combined = cv2.magnitude(sobelx, sobely)
    sobel_8bit = np.uint8(np.absolute(sobel_combined))
    return sobel_8bit

LOGGER = logging.getLogger(__name__)
SHAPES_CAPTCHA_SAMPLE_PATH = "./src/tiktok_live_studio_captcha_solver/resources/shapes_template.png"
SHAPES_TEMPLATE_MASK_PATH = "./src/tiktok_live_studio_captcha_solver/resources/shapes_template_mask.png"

SHAPES_TEMPLATE_BASE = cv2.imread(
    SHAPES_CAPTCHA_SAMPLE_PATH,
    cv2.IMREAD_GRAYSCALE
)

if SHAPES_TEMPLATE_BASE is None:
    raise ValueError("Could not load shapes captcha sample image at " + SHAPES_CAPTCHA_SAMPLE_PATH)
SHAPES_TEMPLATE = sobel(SHAPES_TEMPLATE_BASE)

SHAPES_TEMPLATE_MASK = cv2.imread(
    SHAPES_TEMPLATE_MASK_PATH,
    cv2.IMREAD_GRAYSCALE
)

if SHAPES_TEMPLATE_MASK is None:
    raise ValueError("Could not load shapes captcha template mask at " + SHAPES_CAPTCHA_SAMPLE_PATH)

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
    image: Image.Image
) -> Box:
    """Find the area of the shapes captcha image as PIL image as a pyscreeze box"""

    mat = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
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
    cv2.imwrite("./images/test_shapes_captcha_match.png", mat)
    cv2.imwrite("./images/test_shapes_template.png", SHAPES_TEMPLATE)
    box = Box(left=top_left[0], top=top_left[1], width=w, height=h )
    LOGGER.debug("found shapes captcha box at " + box.__repr__())
    return box
