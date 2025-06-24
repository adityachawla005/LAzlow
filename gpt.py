import requests
import re
import os
import time
from datetime import datetime
from intent_classifier import predict_intent, extract_entities
from os_actions import (
    confirm_dialog,
    type_text,
    press_hotkey,
    delete_path,
    move_mouse_to,
    click_mouse,
    detect_and_activate_button,
    control_volume,
    close_application
)

SERP_API_KEY = "5ff080f9f8b3182c00c09d251a0f064f50208586074335f5e47bced15fbbdd7c"
DEBUG = True
assistant_locked = False

LOG_DIR = os.path.expanduser("~/Lazlow/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"lazlow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def log_debug(msg):
    if DEBUG:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} - {msg}\n")
        except Exception as e:
            print(f"[LOGGING ERROR] {e}")

def split_into_commands(user_input):
    return [p.strip() for p in re.split(r'\s+and\s+|\s*,\s*', user_input.strip(), flags=re.IGNORECASE) if p]

def is_ollama_online():
    try:
        r = requests.get("http://localhost:11434", timeout=2)
        return r.status_code == 200
    except:
        return False

def handle_intent(user_input):
    global assistant_locked

    try:
        cleaned_input = user_input.strip().lower()
        if cleaned_input == "wake up":
            assistant_locked = False
            return "Lazlow is listening again."

        intent = predict_intent(user_input)
        entity = extract_entities(user_input, intent)
        log_debug(f"[INTENT] {intent} | [ENTITY] {entity}")

        if assistant_locked:
            return "Lazlow is vibing... Say 'wake up' to continue."

        match intent:
            case "vibe":
                assistant_locked = True
                detect_and_activate_button("vibe")
                return "Starting the vibe on Spotify."

            case "navigate":
                detect_and_activate_button("navigate")
                return "Searching..."

            case "confirm_yes":
                return confirm_dialog("yes")

            case "close_application":
                return close_application(entity)

            case "confirm_no":
                return confirm_dialog("no")

            case "open_app":
                press_hotkey("ctrl", "alt", "t")   # Open terminal
                time.sleep(2)                      # Wait 2 seconds for terminal to open
                type_text(entity)                  # Type the app name, e.g. "spotify"
                press_hotkey("enter")  
                return f"Opened and ran '{entity}'."

            case "type_text":
                type_text(entity)
                return f"Typed: {entity}"

            case "press_keys":
                keys = entity.replace("+", " ").split()
                return press_hotkey(*keys)

            case "delete_file":
                return delete_path(entity)

            case "move_mouse":
                try:
                    x, y = map(int, entity.split(","))
                    return move_mouse_to(x, y)
                except Exception as e:
                    log_debug(f"[MOUSE COORD ERROR] {e}")
                    return "Invalid mouse coordinates."

            case "click_mouse":
                return click_mouse()

            case "double_click":
                from os_actions import double_click
                return double_click()

            case "right_click":
                from os_actions import right_click
                return right_click()

            case "select_all":
                from os_actions import select_all
                return select_all()

            case "copy_text":
                from os_actions import copy
                return copy()

            case "paste_text":
                from os_actions import paste
                return paste()

            case "press_delete":
                from os_actions import delete
                return delete()

            case "drag_mouse":
                from os_actions import drag_mouse_to
                try:
                    x, y = map(int, entity.split(","))
                    return drag_mouse_to(x, y)
                except Exception as e:
                    log_debug(f"[DRAG COORD ERROR] {e}")
                    return "Invalid drag coordinates."

            case "scroll_mouse":
                from os_actions import scroll_mouse
                direction = entity.lower().strip() if entity else "up"
                return scroll_mouse(direction)

            case "volume_control":
                original_input = user_input.lower()
                if any(word in original_input for word in ["volume", "sound", "louder", "softer", "quieter", "mute", "increase", "decrease"]):
                    if "up" in original_input or "increase" in original_input or "louder" in original_input:
                        return control_volume("up")
                    elif "down" in original_input or "decrease" in original_input or "quieter" in original_input:
                        return control_volume("down")
                elif "mute" in original_input:
                        return control_volume("mute")
                log_debug(f"[VOLUME INTENT IGNORED] Input: {original_input}")
                return None


            case "unknown":
                return None

            case _:
                return None
    except Exception as e:
        log_debug(f"[INTENT ERROR] {e}")
        return "There was a problem processing your command."

def fallback_web_search(query):
    try:
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get("https://api.duckduckgo.com/", params=params, timeout=8)
        data = response.json()

        answer = data.get("AbstractText") or data.get("Answer") or data.get("Definition") or ""
        related_topics = data.get("RelatedTopics", [])

        if answer:
            result = answer
        elif related_topics:
            first_topic = related_topics[0]
            if isinstance(first_topic, dict):
                result = first_topic.get("Text", "")
            else:
                result = ""
        else:
            result = "Sorry, I couldn't find anything useful online."

        log_debug(f"[DUCKDUCKGO RESULT] {result}")
        return result
    except Exception as e:
        log_debug(f"[DUCKDUCKGO ERROR] {e}")
        return "I couldn't access the internet right now."

def ask_gpt(user_input):
    responses = []

    for cmd in split_into_commands(user_input):
        result = handle_intent(cmd)
        if result:
            responses.append(result)

    if responses:
        log_debug(f"[INTENT RESULT] {responses}")
        return " ".join(responses)

    log_debug("[INTENT FALLBACK] No valid intent matched, trying web then Ollama...")

    # 🌐 DuckDuckGo fallback (always try first)
    try:
        web_result = fallback_web_search(user_input)
        if web_result and web_result.strip() and "couldn't" not in web_result.lower():
            return web_result
    except Exception as e:
        log_debug(f"[WEB FALLBACK ERROR] {e}")

    # 🧠 Ollama fallback
    try:
        log_debug(f"[OLLAMA PROMPT] {user_input}")
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            json={
                "model": "mistral",
                "prompt": user_input,
                "stream": False
            },
            timeout=30
        )
        data = response.json()
        reply = data.get("response", "").strip()
        log_debug(f"[OLLAMA RESPONSE] {reply}")
        return reply or "Sorry, I didn’t find anything useful."
    except requests.exceptions.ReadTimeout:
        return "Ollama took too long to respond. Try again."
    except Exception as e:
        log_debug(f"[OLLAMA ERROR] {e}")
        return "Something went wrong while thinking about that."
