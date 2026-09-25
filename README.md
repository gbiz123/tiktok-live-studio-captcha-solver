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
This tool uses `pyautogui` to take screenshots and to move and click the mouse.
On Windows and macOS, the operating system blocks those actions unless the terminal you launch from has
been granted the right permissions, so follow the steps for your OS below.
If the permissions are missing, the solver usually appears to run fine but the clicks silently do nothing,
or the screenshots come back blank/black.

### Windows
1. Press the Start button and type `cmd` (or `powershell`).
2. Right click the result and choose **Run as administrator**, then accept the UAC prompt.
3. In that administrator terminal, run:
   ```
   python -m tiktok_live_studio_captcha_solver
   ```

### macOS
macOS requires you to explicitly allow the terminal app to control the mouse and to record the screen:

1. Open **System Settings → Privacy & Security → Accessibility** and enable your terminal app
   (Terminal, iTerm2, VS Code, etc.). Use the `+` button to add it if it is not listed.
2. Open **System Settings → Privacy & Security → Screen Recording** and enable the same app.
3. Quit and reopen the terminal app completely — the new permissions only apply to a freshly launched process.
4. Run:
   ```
   python -m tiktok_live_studio_captcha_solver
   ```

The first time the solver takes a screenshot or moves the mouse, macOS may show a permission prompt.
Approve it, then restart the terminal and run the command again.

### Linux
No special permissions are needed. Make sure `gnome-screenshot` is installed, then run:
```
python -m tiktok_live_studio_captcha_solver
```
If you are on Wayland, run your session under X11 instead — `pyautogui` cannot move the mouse or capture
the screen under Wayland.

Once the solver is running, TikTok Live Studio captchas will be solved automatically. Leave the terminal
window open while you stream.

## Logging
You may set the log level at runtime with the LOG_LEVEL environment variable.
For example, to set to INFO you would want to set `LOG_LEVEL=INFO` when you run the program.
You can also enable image logging by setting `LOG_IMAGES=true` when you run the program.

## Support us
<a href="https://www.buymeacoffee.com/gbiz123" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
