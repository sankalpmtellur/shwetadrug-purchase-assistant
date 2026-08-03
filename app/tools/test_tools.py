from app.tools.mouse_tracker import track_mouse
from app.tools.screenshot_tool import take_screenshot
from app.tools.window_detector import list_open_windows


def show_menu():
    print("Inspection Toolkit")
    print("1. Detect Windows")
    print("2. Mouse Tracker")
    print("3. Screenshot")


def run_selected_tool(selection):
    if selection == "1":
        return list_open_windows()
    if selection == "2":
        return track_mouse()
    if selection == "3":
        return take_screenshot()

    print("Invalid selection.")
    return None


def main():
    show_menu()
    selection = input("Select a tool: ").strip()
    run_selected_tool(selection)


if __name__ == "__main__":
    main()
