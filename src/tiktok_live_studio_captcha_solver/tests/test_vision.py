from PIL import Image

from ..vision import find_shapes_captcha_box

def test_find_shapes_captcha_box():
    img = Image.open("./images/image1.png") 
    box = find_shapes_captcha_box(img)

def test_find_shapes_captcha_box_when_not_present_throws_error():
    could_not_find_template_exception_thrown = False
    try:
        img = Image.open("./images/unrelated.png") 
        box = find_shapes_captcha_box(img)
    except Exception as e:
        could_not_find_template_exception_thrown = True
    assert could_not_find_template_exception_thrown
