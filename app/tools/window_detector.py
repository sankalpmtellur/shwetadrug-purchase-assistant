from pywinauto import Desktop


def list_open_windows():
    windows = Desktop(backend="uia").windows(visible_only=False)
    window_details = []

    for window in windows:
        title = window.window_text()
        visible = window.is_visible()
        window_details.append({"title": title, "visible": visible})

        print(f"Window title: {title}")
        print(f"Visible: {visible}")
        print()

    return window_details


if __name__ == "__main__":
    list_open_windows()
