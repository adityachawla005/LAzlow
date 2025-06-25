import os
import platform
import subprocess
import pyautogui
import shutil
import time
import random

def open_anything(app_or_path):
    system = platform.system()

    known_locations = {
        "downloads": os.path.expanduser("~/Downloads"),
        "documents": os.path.expanduser("~/Documents"),
        "pictures": os.path.expanduser("~/Pictures"),
        "music": os.path.expanduser("~/Music"),
        "videos": os.path.expanduser("~/Videos"),
        "desktop": os.path.expanduser("~/Desktop"),
    }

    app_or_path = app_or_path.lower().strip()
    app_or_path = known_locations.get(app_or_path, app_or_path)

    try:
        if app_or_path == "terminal":
            if system == "Linux":
                for terminal in ["gnome-terminal", "konsole", "x-terminal-emulator", "xterm"]:
                    try:
                        subprocess.Popen([terminal])
                        return f"Opening {terminal}"
                    except FileNotFoundError:
                        continue
                return "No terminal app found on this system."
            elif system == "Windows":
                subprocess.Popen(["cmd"])
                return "Opening Command Prompt"
            elif system == "Darwin":
                subprocess.run(["open", "-a", "Terminal"])
                return "Opening Terminal"
        else:
            if system == "Windows":
                os.startfile(app_or_path)
            elif system == "Darwin":
                subprocess.run(["open", app_or_path], check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", app_or_path], check=True)
            else:
                return "Unsupported operating system."
            return f"Opening {app_or_path}"
    except Exception as e:
        return f"Failed to open {app_or_path}: {e}"


def confirm_dialog(choice):
    choice = choice.lower()
    if choice == "yes":
        pyautogui.press("enter")
        return "Clicked Yes."
    elif choice == "no":
        pyautogui.press("esc")
        return "Clicked No."
    else:
        return "I didn't understand the confirmation choice."


def type_text(text):
    time.sleep(1.5)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(text, interval=0.05)


def move_mouse_to(x, y):
    pyautogui.moveTo(x, y, duration=0.5)
    return f"Moved mouse to ({x}, {y})"


def click_mouse():
    pyautogui.click()
    return "Mouse clicked."


def double_click():
    pyautogui.doubleClick()
    return "Mouse double-clicked."


def right_click():
    pyautogui.rightClick()
    return "Mouse right-clicked."


def select_all():
    pyautogui.hotkey('ctrl', 'a')
    return "Selected all."


def copy():
    pyautogui.hotkey('ctrl', 'c')
    return "Copied to clipboard."


def paste():
    pyautogui.hotkey('ctrl', 'v')
    return "Pasted from clipboard."


def delete():
    pyautogui.press('delete')
    return "Pressed delete."


def press_hotkey(*keys):
    pyautogui.hotkey(*keys)
    return f"Pressed hotkey: {' + '.join(keys)}"


def delete_path(path):
    try:
        path = os.path.abspath(path)
        if path in ["/", os.path.expanduser("~")]:
            return "Refused to delete critical system directory."

        if os.path.isfile(path):
            os.remove(path)
            return f"Deleted file: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Deleted folder: {path}"
        else:
            return "Path doesn't exist."
    except Exception as e:
        return f"Error deleting {path}: {e}"

def scroll_mouse(direction):
    try:
        if direction == "up":
            pyautogui.scroll(100)
            return "Scrolled up by 100 units."
        elif direction == "down":
            pyautogui.scroll(-100)
            return "Scrolled down by 100 units."
        else:
            return "Invalid scroll direction. Use 'up' or 'down'."
    except Exception as e:
        return f"Scroll failed: {e}"



def drag_mouse_to(x, y):
    try:
        pyautogui.dragTo(x, y, duration=0.5)
        return f"Dragged mouse to ({x}, {y})"
    except Exception as e:
        return f"Drag failed: {e}"


def detect_and_activate_button(command):
    button_coords = {
        "vibe": (532, 293),
        "navigate": (917, 99)
    }

    command = command.lower()
    if command not in button_coords:
        return "Unknown command. Use 'vibe' or 'navigate'."

    x, y = button_coords[command]
    jitter_x = random.randint(-5, 5)
    jitter_y = random.randint(-5, 5)
    final_x = x + jitter_x
    final_y = y + jitter_y

    pyautogui.moveTo(final_x, final_y, duration=0.4)
    pyautogui.click()
    return f"Clicked button for: {command}"



def control_volume(action):
    try:
        if platform.system() == "Linux":
            if action == "up":
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
                return "Volume increased."
            elif action == "down":
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
                return "Volume decreased."
            elif action == "mute":
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])
                return "Volume muted."
            elif action == "unmute":
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])
                return "Volume unmuted."
            else:
                return "Unknown volume command."
        else:
            return "Volume control not implemented for this OS."
    except Exception as e:
        return f"Volume control failed: {e}"


def close_application(app_name):
    try:
        app_name = app_name.lower().strip()
        if platform.system() == "Linux":
            subprocess.run(["pkill", "-f", app_name])
        elif platform.system() == "Windows":
            subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], shell=True)
        elif platform.system() == "Darwin":
            subprocess.run(["osascript", "-e", f'tell application "{app_name}" to quit'])
        else:
            return "Unsupported operating system."
        return f"Attempted to close {app_name}."
    except Exception as e:
        return f"Failed to close {app_name}: {e}"
