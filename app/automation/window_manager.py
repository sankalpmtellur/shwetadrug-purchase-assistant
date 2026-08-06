import time

from app.automation.config import POLL_INTERVAL, STARTUP_TIMEOUT, WINDOW_TITLE
from app.tools.logger import get_logger


logger = get_logger(__name__)


def log_action(action, success, message=""):
    status = "Success" if success else "Failure"
    detail = f" | {message}" if message else ""
    logger.info("Action: %s | Result: %s%s", action, status, detail)


def find_pharma_window(title=WINDOW_TITLE):
    try:
        import pygetwindow as gw
    except ImportError as error:
        log_action("Find Pharma window", False, f"pygetwindow unavailable: {error}")
        return None

    matches = [
        window
        for window in gw.getAllWindows()
        if title.lower() in window.title.lower()
    ]

    if matches:
        log_action("Find Pharma window", True, matches[0].title)
        return matches[0]

    log_action("Find Pharma window", False, f"No window title contains '{title}'")
    return None


def is_pharma_running(title=WINDOW_TITLE):
    window = find_pharma_window(title)
    return window is not None


def get_window_title(title=WINDOW_TITLE):
    window = find_pharma_window(title)
    if not window:
        return None

    log_action("Get Pharma window title", True, window.title)
    return window.title


def bring_pharma_to_front(title=WINDOW_TITLE):
    window = find_pharma_window(title)
    if not window:
        log_action("Bring Pharma window to front", False, "Window not found")
        return False

    try:
        if getattr(window, "isMinimized", False):
            window.restore()

        window.activate()
        log_action("Bring Pharma window to front", True, window.title)
        return True
    except Exception as error:
        log_action("Bring Pharma window to front", False, str(error))
        return False


def maximize_pharma_window(title=WINDOW_TITLE):
    window = find_pharma_window(title)
    if not window:
        log_action("Maximize Pharma window", False, "Window not found")
        return False

    try:
        if getattr(window, "isMinimized", False):
            window.restore()

        window.maximize()
        log_action("Maximize Pharma window", True, window.title)
        return True
    except Exception as error:
        log_action("Maximize Pharma window", False, str(error))
        return False


def wait_for_window(window_title=WINDOW_TITLE, timeout=STARTUP_TIMEOUT, poll_interval=POLL_INTERVAL):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if find_pharma_window(window_title):
            log_action("Wait for window", True, window_title)
            return True

        time.sleep(poll_interval)

    log_action("Wait for window", False, f"Timed out waiting for '{window_title}'")
    return False


def wait_for_window_closed(
    window_title=WINDOW_TITLE,
    timeout=STARTUP_TIMEOUT,
    poll_interval=POLL_INTERVAL,
):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if not find_pharma_window(window_title):
            log_action("Wait for window closed", True, window_title)
            return True

        time.sleep(poll_interval)

    log_action("Wait for window closed", False, f"Timed out waiting for '{window_title}'")
    return False
