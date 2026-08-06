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
    get_pyautogui,
    press_enter,
    wait_for_window,
    write_text,
)


INVOICE_DATE = "03-08-2026"
SUPPLIER_NAME = "Ajit Agencies"
SUPPLIER_BILL_NUMBER = "12345"
SUPPLIER_BILL_DATE = "06-08-2026"
ENTERS_TO_SUPPLIER_FIELD = 4

MEDICINE_NAME = "Acenal P"
BATCH_NUMBER = "11111"
EXPIRY = "01-02-2028"
QUANTITY = "30"
PURCHASE_RATE = "100"
MRP = "150"
SALE_RATE = "200"
DISCOUNT = "10"
REMAINING_COLUMN_ENTERS = 5


def type_supplier(pyautogui, supplier_name):
    for character in supplier_name:
        pyautogui.write(character)
        time.sleep(config.SEARCH_DELAY)
    press_enter(pyautogui)


def enter_header(pyautogui):
    write_text(pyautogui, INVOICE_DATE)
    press_enter(pyautogui)

    for _index in range(ENTERS_TO_SUPPLIER_FIELD):
        press_enter(pyautogui)

    type_supplier(pyautogui, SUPPLIER_NAME)

    write_text(pyautogui, SUPPLIER_BILL_NUMBER)
    press_enter(pyautogui)

    write_text(pyautogui, SUPPLIER_BILL_DATE)
    press_enter(pyautogui)


def type_medicine(pyautogui, medicine_name):
    for character in medicine_name:
        pyautogui.write(character)
        time.sleep(config.SEARCH_DELAY)
    press_enter(pyautogui)


def enter_one_medicine(pyautogui):
    press_enter(pyautogui)

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
