def get_open_window_objects():
    try:
        from pywinauto import Desktop
    except ImportError as error:
        print(f"Window detector unavailable: {error}")
        return []

    return Desktop(backend="uia").windows(visible_only=False)


def list_open_windows():
    windows = get_open_window_objects()
    window_details = []

    for window in windows:
        title = window.window_text()
        visible = window.is_visible()
        window_details.append({"title": title, "visible": visible})

        print(f"Window title: {title}")
        print(f"Visible: {visible}")
        print()

    return window_details


def normalize_title(title):
    return " ".join(str(title).upper().split())


def window_title_matches(configured_title, current_title):
    configured = normalize_title(configured_title)
    current = normalize_title(current_title)
    return configured in current


def find_window_by_title(configured_title, print_debug=True):
    matched_window = None

    for window in get_open_window_objects():
        current_title = window.window_text()
        match = window_title_matches(configured_title, current_title)

        if print_debug:
            print("Checking:")
            print(current_title)
            print()
            print("Configured:")
            print(configured_title)
            print()
            print("Current:")
            print(current_title)
            print()
            print("Match:")
            print(match)
            print()

        if match and matched_window is None:
            matched_window = window

    return matched_window


def focus_window(window):
    try:
        if hasattr(window, "is_minimized") and window.is_minimized():
            window.restore()

        if hasattr(window, "set_focus"):
            window.set_focus()

        if hasattr(window, "is_minimized") and window.is_minimized():
            window.maximize()

        return True
    except Exception as error:
        print(f"Focus Error: {error}")
        return False


if __name__ == "__main__":
    list_open_windows()
