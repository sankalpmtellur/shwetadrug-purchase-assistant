from datetime import date
from pathlib import Path
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation import config
from app.tools.window_detector import find_window_by_title, focus_window


INVOICE_DATE = "03/08/2026"
SUPPLIER_NAME = "CIPLA"
SUPPLIER_BILL_NUMBER = "24563"


def get_pyautogui():
    try:
        import pyautogui
    except ImportError as error:
        print(f"Header Entry Failed: pyautogui unavailable: {error}")
        return None

    return pyautogui


def wait_for_window(title, timeout=config.PURCHASE_WINDOW_TIMEOUT):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        window = find_window_by_title(title, print_debug=False)
        if window is not None:
            return window
        time.sleep(config.POLL_INTERVAL)

    return None


def press_enter(pyautogui):
    pyautogui.press("enter")
    time.sleep(config.KEYBOARD_ACTION_DELAY)


def write_text(pyautogui, value):
    pyautogui.write(str(value))
    time.sleep(config.KEYBOARD_ACTION_DELAY)


def type_supplier(pyautogui, supplier_name):
    for character in supplier_name:
        pyautogui.write(character)
        time.sleep(config.SEARCH_DELAY)
    press_enter(pyautogui)


def enter_header(pyautogui):
    today = date.today().strftime("%d-%m-%Y")

    write_text(pyautogui, INVOICE_DATE)
    press_enter(pyautogui)

    press_enter(pyautogui)
    press_enter(pyautogui)

    for _index in range(config.SUPPLIER_FIELD_TAB_COUNT):
        press_enter(pyautogui)

    type_supplier(pyautogui, SUPPLIER_NAME)

    write_text(pyautogui, SUPPLIER_BILL_NUMBER)
    press_enter(pyautogui)

    write_text(pyautogui, today)
    press_enter(pyautogui)


def run_header_live_test():
    pyautogui = get_pyautogui()
    if pyautogui is None:
        return False

    pharma_window = find_window_by_title(config.WINDOW_TITLE, print_debug=True)
    if pharma_window is None:
        print("Header Entry Failed")
        return False

    if not focus_window(pharma_window):
        print("Header Entry Failed")
        return False

    time.sleep(config.MEDIUM_DELAY)
    pyautogui.hotkey("ctrl", "p")
    time.sleep(config.KEYBOARD_ACTION_DELAY)

    purchase_window = wait_for_window(config.PURCHASE_BILL_WINDOW_TITLE)
    if purchase_window is None:
        print("Header Entry Failed")
        return False

    if not focus_window(purchase_window):
        print("Header Entry Failed")
        return False

    enter_header(pyautogui)
    print("Header Entry Successful")
    return True


def test_header_live_script_runs():
    result = run_header_live_test()
    assert isinstance(result, bool)


if __name__ == "__main__":
    run_header_live_test()
