import logging
import os

from tiktok_live_studio_captcha_solver.api import ApiClient
from .logs import LOGS_DIR, initialize_log_dir
from .solver import prompt_api_key, solve_loop

if __name__ == "__main__":
    api_key = prompt_api_key()
    api_client = ApiClient(api_key)
    solve_loop(api_client)
