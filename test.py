import threading
import pyttsx3

def speak(text):
    engine = pyttsx3.init()  # Init inside thread
    engine.say(text)
    engine.runAndWait()

def speak_in_background(text):
    thread = threading.Thread(target=speak, args=(text,))
    thread.start()
    return thread

# Usage
thread = speak_in_background("Signing off. Have a nice day.")
thread.join()
