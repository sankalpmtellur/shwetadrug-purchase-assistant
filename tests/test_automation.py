from pathlib import Path
import sys
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.automation_engine import PurchaseAutomation
from app.automation import keyboard_controller
from app.automation.window_manager import is_pharma_running


class FakePyAutoGUI:
    def write(self, text, interval=0):
        return None

    def press(self, key):
        return None

    def hotkey(self, *keys):
        return None


def test_window_detection_works():
    result = is_pharma_running()
    print(f"Pharma running: {result}")
    assert isinstance(result, bool)


def test_keyboard_helpers_execute_without_exceptions():
    fake_pyautogui = FakePyAutoGUI()

    with patch.dict(sys.modules, {"pyautogui": fake_pyautogui}):
        assert keyboard_controller.write("test") is True
        assert keyboard_controller.press_enter() is True
        assert keyboard_controller.press_tab() is True
        assert keyboard_controller.press_ctrl_p() is True
        assert keyboard_controller.press_down() is True
        assert keyboard_controller.press_up() is True
        assert keyboard_controller.press_escape() is True
        assert keyboard_controller.hotkey("ctrl", "s") is True

    with patch("time.sleep", return_value=None):
        assert keyboard_controller.small_delay() is True
        assert keyboard_controller.medium_delay() is True
        assert keyboard_controller.large_delay() is True


def test_automation_object_initializes():
    automation = PurchaseAutomation()
    assert isinstance(automation, PurchaseAutomation)


if __name__ == "__main__":
    test_window_detection_works()
    test_keyboard_helpers_execute_without_exceptions()
    test_automation_object_initializes()
