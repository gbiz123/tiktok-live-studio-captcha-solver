from PIL import Image

from ..vision import find_shapes_captcha_box

def test_find_shapes_captcha_box():
    img = Image.open("./images/image3.png") 
    box = find_shapes_captcha_box(img)
