from PIL import Image

from ..vision import extract_puzzle_canvas, find_puzzle_captcha_box, find_shapes_captcha_box, find_slide_button_box

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

def test_find_slide_button_box():
    img = Image.open("./images/puzzle_slide.png")
    box = find_slide_button_box(img)

def test_find_puzzle_captcha_box():
    img = Image.open("./images/puzzle_slide.png")
    box = find_puzzle_captcha_box(img)

def test_extract_puzzle_canvas():
    img = Image.open("./images/puzzle_slide.png")
    canvas = extract_puzzle_canvas(img)
    canvas.save("./images/test_extract_canvas.png")


