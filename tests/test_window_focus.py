from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.config import WINDOW_TITLE
from app.tools.window_detector import find_window_by_title, focus_window


def focus_pharma_window():
    print("Configured WINDOW_TITLE:")
    print(WINDOW_TITLE)
    print()

    window = find_window_by_title(WINDOW_TITLE, print_debug=True)
    window_found = window is not None
    print(f"Window Found: {window_found}")

    if not window_found:
        print("Window Focused Successfully: False")
        print("Window Title: Not Found")
        return False

    focused_successfully = focus_window(window)
    window_title = window.window_text() or "Unknown"

    print(f"Window Focused Successfully: {focused_successfully}")
    print(f"Window Title: {window_title}")

    return focused_successfully


def test_window_focus_script_runs():
    result = focus_pharma_window()
    assert isinstance(result, bool)


if __name__ == "__main__":
    focus_pharma_window()
