from PIL import Image
from tiktok_live_studio_captcha_solver.image_io import pil_to_b64_string

def test_pil_to_b64_string():
    img = Image.open("./images/image1.png")
    assert len(pil_to_b64_string(img)) > 0
