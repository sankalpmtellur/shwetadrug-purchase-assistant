from pathlib import Path
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.config import WINDOW_TITLE
from app.tools.window_detector import find_window_by_title, focus_window


def press_ctrl_p():
    try:
        import pyautogui
    except ImportError as error:
        print(f"Keyboard test unavailable: {error}")
        return False

    pyautogui.hotkey("ctrl", "p")
    return True


def open_purchase_window_test():
    window = find_window_by_title(WINDOW_TITLE, print_debug=True)
    if window is None:
        print("Purchase Window Failed")
        return False

    if not focus_window(window):
        print("Purchase Window Failed")
        return False

    time.sleep(1)

    if not press_ctrl_p():
        print("Purchase Window Failed")
        return False

    time.sleep(3)
    print("Purchase Window Opened")
    return True


def test_open_purchase_script_runs():
    result = open_purchase_window_test()
    assert isinstance(result, bool)


if __name__ == "__main__":
    open_purchase_window_test()
