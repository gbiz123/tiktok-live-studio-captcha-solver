from datetime import datetime
import logging
import os

from PIL import Image

LOGS_DIR = "tiktok-captcha-solver-logs"
IMAGE_LOGS_DIR = os.path.join(LOGS_DIR, "images")
LOGGER = logging.getLogger(__name__)
IS_LOGGING_IMAGES = bool(os.environ.get("LOG_IMAGES"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    filename=os.path.join(LOGS_DIR, "ttls-captcha-solver.log"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def initialize_log_dir():
    if not os.path.isdir(LOGS_DIR):
        os.mkdir(LOGS_DIR)
        os.mkdir(IMAGE_LOGS_DIR)
        LOGGER.debug("initialized log directories")
    else:
        LOGGER.debug("log directories already exist")

def log_image(image: Image.Image, filename: str) -> None:
    if IS_LOGGING_IMAGES:
        timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
        name, extension = filename.split(".")
        new_filename = name + "_" + timestamp + "." + extension
        image.save(os.path.join(IMAGE_LOGS_DIR, new_filename))
        LOGGER.debug("saved image to " + new_filename)
    else:
        LOGGER.debug("not logging image. To log images, set IS_LOGGING_IMAGES=1 environment variable.")
