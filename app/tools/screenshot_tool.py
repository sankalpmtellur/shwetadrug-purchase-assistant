from datetime import datetime
from pathlib import Path

import pyautogui


SCREENSHOT_DIR = Path("screenshots")


def take_screenshot():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
    output_path = SCREENSHOT_DIR / filename

    screenshot = pyautogui.screenshot()
    screenshot.save(output_path)

    print(f"Screenshot saved: {output_path}")
    return output_path


if __name__ == "__main__":
    take_screenshot()
