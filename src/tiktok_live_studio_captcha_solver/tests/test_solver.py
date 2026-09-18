import os

from ..api import ApiClient
from ..solver import solve_puzzle_captcha, solve_shapes_captcha

def test_solve_shapes_captcha():
    api_key = os.environ["API_KEY"]
    api_client = ApiClient(api_key)
    solve_shapes_captcha(api_client)

def test_solve_puzzle_captcha():
    api_key = os.environ["API_KEY"]
    api_client = ApiClient(api_key)
    solve_puzzle_captcha(api_client)
