import time
import traceback

from app.automation import config
from app.tools.logger import get_logger


logger = get_logger(__name__)


def _log_action(action, success, message=""):
    status = "Success" if success else "Failure"
    detail = f" | {message}" if message else ""
    logger.info("Action: %s | Result: %s%s", action, status, detail)


def _run_keyboard_action(action, callback, delay=None):
    try:
        import pyautogui

        callback(pyautogui)
        time.sleep(config.FIELD_DELAY if delay is None else delay)
        _log_action(action, True)
        return True
    except Exception as error:
        _log_action(action, False, str(error))
        traceback.print_exc()
        raise


def write(text):
    return _run_keyboard_action(
        "Write text",
        lambda pyautogui: pyautogui.write(str(text), interval=config.KEY_DELAY),
        delay=config.FIELD_DELAY,
    )


def press_enter():
    return _press("enter")


def press_tab():
    return _press("tab")


def press_ctrl_p():
    return hotkey("ctrl", "p")


def press_down():
    return _press("down")


def press_up():
    return _press("up")


def press_escape():
    return _press("escape")


def hotkey(*keys):
    return _run_keyboard_action(
        f"Hotkey {'+'.join(keys)}",
        lambda pyautogui: pyautogui.hotkey(*keys),
        delay=config.FIELD_DELAY,
    )


def small_delay():
    return _delay("Small delay", config.SHORT_DELAY)


def medium_delay():
    return _delay("Medium delay", config.MEDIUM_DELAY)


def large_delay():
    return _delay("Large delay", config.LONG_DELAY)


def _press(key):
    return _run_keyboard_action(
        f"Press {key}",
        lambda pyautogui: pyautogui.press(key),
        delay=config.KEY_DELAY,
    )


def _delay(action, seconds):
    try:
        time.sleep(seconds)
        _log_action(action, True, f"{seconds}s")
        return True
    except Exception as error:
        _log_action(action, False, str(error))
        return False
