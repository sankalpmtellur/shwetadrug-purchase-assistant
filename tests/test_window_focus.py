from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.config import WINDOW_TITLE
from app.automation.window_manager import (
    bring_pharma_to_front,
    get_window_title,
    is_pharma_running,
    maximize_pharma_window,
)


def focus_pharma_window():
    window_found = is_pharma_running(WINDOW_TITLE)
    print(f"Window Found: {window_found}")

    if not window_found:
        print("Window Focused Successfully: False")
        print("Window Title: Not Found")
        return False

    focused = bring_pharma_to_front(WINDOW_TITLE)
    maximized = maximize_pharma_window(WINDOW_TITLE)
    focused_successfully = focused and maximized
    window_title = get_window_title(WINDOW_TITLE) or "Unknown"

    print(f"Window Focused Successfully: {focused_successfully}")
    print(f"Window Title: {window_title}")

    return focused_successfully


def test_window_focus_script_runs():
    result = focus_pharma_window()
    assert isinstance(result, bool)


if __name__ == "__main__":
    focus_pharma_window()
