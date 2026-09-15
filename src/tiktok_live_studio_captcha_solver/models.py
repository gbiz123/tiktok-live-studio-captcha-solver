from pydantic import BaseModel
from pyscreeze import Box

class ShapesCaptchaResponse(BaseModel):
    point_one_proportion_x: float
    point_one_proportion_y: float
    point_two_proportion_x: float
    point_two_proportion_y: float

class ProportionalPoint(BaseModel):
    proportion_x: float
    proportion_y: float

class IconCaptchaResponse(BaseModel):
    proportional_points: list[ProportionalPoint]

class RotateCaptchaResponse(BaseModel):
    angle: int

class PuzzleCaptchaResponse(BaseModel):
    slide_x_proportion: float

class ImageB64WithBox(BaseModel):
    image_b64: str
    box: Box

