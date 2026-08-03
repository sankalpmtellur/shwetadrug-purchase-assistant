import time

import pyautogui


def track_mouse(interval=0.2):
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Mouse X: {x}")
            print(f"Mouse Y: {y}")
            print()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Mouse tracker stopped.")


if __name__ == "__main__":
    track_mouse()
