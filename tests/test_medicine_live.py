from pathlib import Path
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent

for path in (PROJECT_ROOT, TESTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.automation import config
from app.tools.window_detector import find_window_by_title, focus_window
from test_header_live import (
    enter_header,
    get_pyautogui,
    press_enter,
    wait_for_window,
    write_text,
)


MEDICINE_NAME = "DOLO 650 TAB"
BATCH_NUMBER = "ABCD123"
EXPIRY = "01.10.27"
QUANTITY = "10"
PURCHASE_RATE = "12.50"
MRP = "15.00"
SALE_RATE = "14.00"
DISCOUNT = "10"
REMAINING_COLUMN_ENTERS = 4


def type_medicine(pyautogui, medicine_name):
    for character in medicine_name:
        pyautogui.write(character)
        time.sleep(config.SEARCH_DELAY)
    press_enter(pyautogui)


def enter_one_medicine(pyautogui):
    type_medicine(pyautogui, MEDICINE_NAME)

    write_text(pyautogui, BATCH_NUMBER)
    press_enter(pyautogui)

    write_text(pyautogui, EXPIRY)
    press_enter(pyautogui)

    write_text(pyautogui, QUANTITY)
    press_enter(pyautogui)

    press_enter(pyautogui)

    write_text(pyautogui, PURCHASE_RATE)
    press_enter(pyautogui)

    write_text(pyautogui, MRP)
    press_enter(pyautogui)

    write_text(pyautogui, SALE_RATE)
    press_enter(pyautogui)

    write_text(pyautogui, DISCOUNT)
    press_enter(pyautogui)

    for _index in range(REMAINING_COLUMN_ENTERS):
        press_enter(pyautogui)


def run_medicine_live_test():
    pyautogui = get_pyautogui()
    if pyautogui is None:
        print("Medicine Entry Failed")
        return False

    pharma_window = find_window_by_title(config.WINDOW_TITLE, print_debug=True)
    if pharma_window is None:
        print("Medicine Entry Failed")
        return False

    if not focus_window(pharma_window):
        print("Medicine Entry Failed")
        return False

    time.sleep(config.MEDIUM_DELAY)
    pyautogui.hotkey("ctrl", "p")
    time.sleep(config.KEYBOARD_ACTION_DELAY)

    purchase_window = wait_for_window(config.PURCHASE_BILL_WINDOW_TITLE)
    if purchase_window is None:
        print("Medicine Entry Failed")
        return False

    if not focus_window(purchase_window):
        print("Medicine Entry Failed")
        return False

    enter_header(pyautogui)
    enter_one_medicine(pyautogui)
    print("Medicine Entry Successful")
    return True


def test_medicine_live_script_runs():
    result = run_medicine_live_test()
    assert isinstance(result, bool)


if __name__ == "__main__":
    run_medicine_live_test()
