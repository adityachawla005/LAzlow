from tts import speak, stop_speaking, is_speaking
from gpt import ask_gpt
import speech_recognition as sr
import threading
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
import pyfiglet
import itertools
import os
import ctypes
import contextlib

r = sr.Recognizer()
last_error_time = 0
should_exit = False
console = Console()

@contextlib.contextmanager
def suppress_alsa_errors():
    def _py_error_handler(filename, line, function, err, fmt):
        pass
    ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                          ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
    c_error_handler = ERROR_HANDLER_FUNC(_py_error_handler)
    asound = ctypes.cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

def speak_in_background(text):
    thread = threading.Thread(target=speak, args=(text,), daemon=True)
    thread.start()
    return thread

def resize_ascii_art(ascii_text: str, scale: float = 0.4) -> str:
    if not 0 < scale <= 1:
        raise ValueError("Scale must be between 0 and 1")

    lines = ascii_text.strip().split("\n")
    new_lines = []

    row_skip = max(1, int(1 / scale))
    col_skip = max(1, int(1 / scale))

    for i in range(0, len(lines), row_skip):
        line = lines[i]
        new_line = ''.join(line[j] for j in range(0, len(line), col_skip))
        new_lines.append(new_line)

    return "\n".join(new_lines)

def display_ascii_face(path="ascii_face.txt"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            art = f.read()
        smaller = resize_ascii_art(art, scale=0.4)
        centered = "\n".join(line.center(80) for line in smaller.splitlines())
        console.print(centered, style="bold green")

def display_lazlow_banner():
    console.clear()
    display_ascii_face()
    art = pyfiglet.figlet_format("LAZLOW", font="slant")
    console.print(art, style="bold cyan")
    console.print(Panel("Voice Assistant Lazlow Activated — Awaiting your command...", style="bold blue"))

def thinking_animation(duration=3):
    with Live(Text(" thinking", style="bold magenta"), refresh_per_second=4) as live:
        for frame in itertools.cycle([".", "..", "..."]):
            live.update(Text(f"thinking{frame}", style="bold magenta"))
            time.sleep(0.5)
            duration -= 0.5
            if duration <= 0:
                break

def listen_and_respond():
    global last_error_time, should_exit
    display_lazlow_banner()
    while not should_exit:
        if is_speaking():
            time.sleep(0.1)
            continue

        time.sleep(0.5)  # give mic time to settle after TTS ends

        with suppress_alsa_errors():
            with sr.Microphone() as source:
                try:
                    console.print("\n[cyan]🎤 Listening...[/cyan]")
                    audio = r.listen(source, timeout=1, phrase_time_limit=15)
                except sr.WaitTimeoutError:
                    continue

        try:
            command = r.recognize_google(audio).lower()
            console.print(f"[bold yellow]You said:[/] {command}")
        except sr.UnknownValueError:
            if time.time() - last_error_time > 60:
                if not is_speaking():
                    speak_in_background("Could you repeat that once, sir?")
                    last_error_time = time.time()
            continue
        except sr.RequestError:
            if not is_speaking():
                speak_in_background("Hmm, wondering what happened...")
            continue

        if "done for the day" in command:
            thread = speak_in_background("Signing off. Have a nice day.")
            thread.join()
            time.sleep(3)
            should_exit = True
            break

        elif "stop" in command:
            stop_speaking()
            console.print("Yes sir")

        else:
            stop_speaking()
            thinking_animation()
            response = ask_gpt(command)
            console.print("\n[bold blue] Lazlow:[/bold blue]")
            for char in response:
                print(char, end="", flush=True)
                time.sleep(0.015)
            print()
            speak_in_background(response)

# Greet user and start listening
intro_thread = speak_in_background(
    "Hello. I am Lazlow. Say 'done for the day' to stop. Say 'stop' anytime to interrupt me."
)
intro_thread.join()

listen_and_respond()
