import logging
import base64
from io import BytesIO
from PIL import Image

LOGGER = logging.getLogger(__name__)

def pil_to_b64_string(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    LOGGER.debug("converted PIL image to base64 string")
    return base64_string
