# Tiktok Live Studio Captcha Solver
This package runs in the background to solve TikTok live studio captcha's while you're streaming.
Now, you can go away from keyboard for extended periods of time without having to worry about the captcha.

## Prerequisites
- Tkinter installed on system
- gnome-screenshot installed if using Linux
- An API key from SadCaptcha.com

## Dual-monitor setup
This tool uses `pyautogui`, which currently only supports single-monitor setups.
If you have two or monitors, this tool will not work unless you adjust your setup to only use one monitor.

## Installation
`pip install tiktok-live-studio-captcha-solver`

## Usage
Run `python -m tiktok_live_studio_captcha_solver` in your terminal.
Now, tiktok live studio captchas will be solved automatically.
