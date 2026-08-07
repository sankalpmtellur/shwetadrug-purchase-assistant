import queue
import threading
import time

from app.automation.config import (
    POLL_INTERVAL,
    STARTUP_TIMEOUT,
    WINDOW_OPERATION_TIMEOUT,
    WINDOW_TITLE,
)
from app.tools.logger import get_logger


logger = get_logger(__name__)


def log_action(action, success, message=""):
    status = "Success" if success else "Failure"
    detail = f" | {message}" if message else ""
    logger.info("Action: %s | Result: %s%s", action, status, detail)
    print(f"[WINDOW] {action}: {status}{detail}")


def run_with_timeout(action, callback, timeout=WINDOW_OPERATION_TIMEOUT):
    result_queue = queue.Queue(maxsize=1)

    def worker():
        try:
            result_queue.put((True, callback()))
        except Exception as error:
            result_queue.put((False, error))

    print(f"[WINDOW] {action} started")
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        message = f"Timed out after {timeout}s"
        log_action(action, False, message)
        raise TimeoutError(f"{action} {message}")

    success, result = result_queue.get()
    if not success:
        log_action(action, False, str(result))
        raise result

    print(f"[WINDOW] {action} completed")
    return result


def find_pharma_window(title=WINDOW_TITLE):
    print(f"[WINDOW] Finding Pharma window: {title}")
    try:
        import pygetwindow as gw
    except ImportError as error:
        log_action("Find Pharma window", False, f"pygetwindow unavailable: {error}")
        return None

    try:
        windows = run_with_timeout("Enumerate windows", gw.getAllWindows)
    except Exception as error:
        log_action("Find Pharma window", False, str(error))
        return None

    matches = [
        window
        for window in windows
        if title.lower() in str(window.title).lower()
    ]

    if matches:
        log_action("Find Pharma window", True, matches[0].title)
        return matches[0]

    log_action("Find Pharma window", False, f"No window title contains '{title}'")
    return None


def is_pharma_running(title=WINDOW_TITLE):
    print("[WINDOW] Checking if Pharma is running")
    window = find_pharma_window(title)
    running = window is not None
    print(f"[WINDOW] Pharma running: {running}")
    return running


def get_window_title(title=WINDOW_TITLE):
    window = find_pharma_window(title)
    if not window:
        return None

    log_action("Get Pharma window title", True, window.title)
    return window.title


def bring_pharma_to_front(title=WINDOW_TITLE):
    print("[WINDOW] Focusing Pharma window")
    window = find_pharma_window(title)
    if not window:
        log_action("Bring Pharma window to front", False, "Window not found")
        return False

    try:
        if getattr(window, "isMinimized", False):
            run_with_timeout("Restore Pharma window", window.restore)

        run_with_timeout("Activate Pharma window", window.activate)
        log_action("Bring Pharma window to front", True, window.title)
        return True
    except Exception as error:
        log_action("Bring Pharma window to front", False, str(error))
        return False


def maximize_pharma_window(title=WINDOW_TITLE):
    print("[WINDOW] Maximizing Pharma window")
    window = find_pharma_window(title)
    if not window:
        log_action("Maximize Pharma window", False, "Window not found")
        return False

    try:
        if getattr(window, "isMinimized", False):
            run_with_timeout("Restore Pharma window", window.restore)

        run_with_timeout("Maximize Pharma window", window.maximize)
        log_action("Maximize Pharma window", True, window.title)
        return True
    except Exception as error:
        log_action("Maximize Pharma window", False, str(error))
        return False


def wait_for_window(window_title=WINDOW_TITLE, timeout=STARTUP_TIMEOUT, poll_interval=POLL_INTERVAL):
    print(f"[WINDOW] Waiting for window '{window_title}' up to {timeout}s")
    deadline = time.monotonic() + timeout
    attempt = 1

    while time.monotonic() < deadline:
        print(f"[WINDOW] Wait retry {attempt}: {window_title}")
        if find_pharma_window(window_title):
            log_action("Wait for window", True, window_title)
            return True

        attempt += 1
        time.sleep(poll_interval)

    log_action("Wait for window", False, f"Timed out waiting for '{window_title}'")
    return False


def wait_for_window_closed(
    window_title=WINDOW_TITLE,
    timeout=STARTUP_TIMEOUT,
    poll_interval=POLL_INTERVAL,
):
    print(f"[WINDOW] Waiting for window '{window_title}' to close up to {timeout}s")
    deadline = time.monotonic() + timeout
    attempt = 1

    while time.monotonic() < deadline:
        print(f"[WINDOW] Close wait retry {attempt}: {window_title}")
        if not find_pharma_window(window_title):
            log_action("Wait for window closed", True, window_title)
            return True

        attempt += 1
        time.sleep(poll_interval)

    log_action("Wait for window closed", False, f"Timed out waiting for '{window_title}'")
    return False
