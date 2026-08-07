from pathlib import Path
import sys
import time
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.automation_engine import PurchaseAutomation
from app.automation.window_manager import run_with_timeout, wait_for_window


def test_launch_uses_existing_window_path():
    automation = PurchaseAutomation()

    with patch("app.automation.automation_engine.is_pharma_running", return_value=True), \
        patch("app.automation.automation_engine.bring_pharma_to_front", return_value=True), \
        patch("app.automation.automation_engine.maximize_pharma_window", return_value=True), \
        patch("app.automation.automation_engine.subprocess.Popen") as popen:
        assert automation.launch_pharma() is True
        popen.assert_not_called()


def test_launch_uses_executable_path_when_window_missing():
    automation = PurchaseAutomation()

    with patch("app.automation.automation_engine.is_pharma_running", return_value=False), \
        patch("app.automation.automation_engine.subprocess.Popen") as popen, \
        patch("app.automation.automation_engine.wait_for_window", return_value=True):
        assert automation.launch_pharma() is True
        popen.assert_called_once()


def test_login_sequence():
    automation = PurchaseAutomation()

    with patch.object(automation, "launch_pharma", return_value=True), \
        patch("app.automation.automation_engine.wait_for_window", return_value=True), \
        patch("app.automation.automation_engine.keyboard_controller.write", return_value=True) as write, \
        patch("app.automation.automation_engine.keyboard_controller.press_enter", return_value=True) as enter:
        assert automation.login() is True
        assert write.call_count == 2
        assert enter.call_count == 2


def test_login_timeout_path():
    automation = PurchaseAutomation()

    with patch.object(automation, "launch_pharma", return_value=True), \
        patch("app.automation.automation_engine.wait_for_window", return_value=False), \
        patch("app.automation.automation_engine.keyboard_controller.write") as write:
        assert automation.login() is False
        write.assert_not_called()


def test_wait_for_window_timeout():
    with patch("app.automation.window_manager.find_pharma_window", return_value=None), \
        patch("app.automation.window_manager.time.sleep", return_value=None), \
        patch("app.automation.window_manager.time.monotonic", side_effect=[0, 1, 2]):
        assert wait_for_window("Missing Window", timeout=1, poll_interval=0.1) is False


def test_wait_for_window_success():
    with patch("app.automation.window_manager.find_pharma_window", return_value=Mock()), \
        patch("app.automation.window_manager.time.monotonic", return_value=0):
        assert wait_for_window("Pharma Ultimate", timeout=1, poll_interval=0.1) is True


def test_window_operation_timeout_does_not_hang():
    try:
        run_with_timeout("Slow window call", lambda: time.sleep(0.05), timeout=0.01)
    except TimeoutError as error:
        assert "Slow window call Timed out" in str(error)
    else:
        raise AssertionError("Expected TimeoutError")


if __name__ == "__main__":
    test_launch_uses_existing_window_path()
    test_launch_uses_executable_path_when_window_missing()
    test_login_sequence()
    test_login_timeout_path()
    test_wait_for_window_timeout()
    test_wait_for_window_success()
    test_window_operation_timeout_does_not_hang()
