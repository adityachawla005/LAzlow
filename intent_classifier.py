import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

nltk.download('punkt', quiet=True)

# 🧠 Load intent training data
with open("intent.json", "r", encoding="utf-8") as f:
    intent_data = json.load(f)

texts, labels = [], []
for intent in intent_data:
    for example in intent["examples"]:
        texts.append(example.lower().strip())
        labels.append(intent["intent"])

# ⚙️ ML pipeline: TF-IDF + Logistic Regression
pipeline = make_pipeline(
    TfidfVectorizer(),
    LogisticRegression(max_iter=300)
)

pipeline.fit(texts, labels)

# 🔮 Predict intent from user input
def predict_intent(user_input: str) -> str:
    try:
        return pipeline.predict([user_input.lower().strip()])[0]
    except Exception:
        return "unknown"

# 🧹 Helper: Remove known phrases
def strip_phrases(text: str, phrases: list) -> str:
    for phrase in phrases:
        text = text.replace(phrase, "")
    return text.strip()

def extract_entities(text: str, intent: str) -> str:
    text = text.lower().strip()

    match intent:

        case "open_app":
            phrases = [
                "open terminal and run", "open terminal and type",
                "launch terminal and run", "launch terminal and open",
                "start", "run", "open", "launch", "in terminal", "and run"
            ]
            return strip_phrases(text, phrases)

        case "close_application":
            return strip_phrases(text, ["close", "shut down", "exit", "terminate", "quit", "kill"])

        case "type_text":
            return strip_phrases(text, ["type", "write", "input", "write down", "type in"])

        case "press_keys":
            return strip_phrases(text, ["press", "press keys", "press the keys", "press hotkey"])

        case "delete_file":
            return strip_phrases(text, ["delete", "remove", "erase", "delete file", "remove file"])

        case "move_mouse":
            return strip_phrases(text, ["move mouse to", "move cursor to", "move to", "cursor to", "pointer to"])

        case "drag_mouse":
            return strip_phrases(text, ["drag mouse to", "drag cursor to", "drag to"])

        case "scroll_mouse":
            if "down" in text:
                return "down"
            elif "up" in text:
                return "up"
            else:
                return "up"  # default direction

        case "volume_control":
            if "up" in text or "increase" in text or "raise" in text:
                return "up"
            elif "down" in text or "decrease" in text or "reduce" in text:
                return "down"
            elif "mute" in text or "unmute" in text:
                return "mute"
            else:
                return "unknown"

        case "press_delete":
            return ""  # no entity needed

        case "click_mouse":
            return ""  # no entity needed

        case "double_click":
            return ""  # no entity needed

        case "right_click":
            return ""  # no entity needed

        case "select_all":
            return ""  # no entity needed

        case "copy_text":
            return ""  # no entity needed

        case "paste_text":
            return ""  # no entity needed

        case "confirm_yes":
            return "yes"

        case "confirm_no":
            return "no"

        case "navigate":
            return ""  # button-based

        case "vibe":
            return ""  # button-based

        case "wake_up":
            return ""  # internal control

        case "stop_spotify":
            return ""  # internal control

        case _:
            return strip_phrases(text, ["please", "could you", "can you", "would you", "kindly", "just"])
