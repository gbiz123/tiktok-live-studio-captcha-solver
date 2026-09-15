import logging

from tiktok_live_studio_captcha_solver.api import ApiClient
from tiktok_live_studio_captcha_solver.solver import prompt_api_key, solve_loop

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    api_key = prompt_api_key()
    api_client = ApiClient(api_key)
    solve_loop(api_client)
