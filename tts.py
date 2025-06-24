import asyncio
import edge_tts
import threading
import os
import hashlib
from pydub import AudioSegment
import simpleaudio as sa
import time

CACHE_DIR = "cache_audio"
VOICE = "en-GB-RyanNeural"

speak_lock = threading.Lock()
current_play_obj = None
should_stop = threading.Event()
is_currently_speaking = threading.Event()

os.makedirs(CACHE_DIR, exist_ok=True)

def is_speaking():
    return is_currently_speaking.is_set()

def get_cache_path(text):
    normalized = text.strip().lower()
    text_hash = hashlib.md5(normalized.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.wav")

def stop_current_playback():
    global current_play_obj
    with speak_lock:
        if current_play_obj and current_play_obj.is_playing():
            current_play_obj.stop()

def play_audio(file_path, after_speak=None):
    global current_play_obj
    if should_stop.is_set():
        return

    with speak_lock:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        current_play_obj = wave_obj.play()
        is_currently_speaking.set()

    while current_play_obj.is_playing():
        if should_stop.is_set():
            current_play_obj.stop()
            break
        time.sleep(0.01)

    is_currently_speaking.clear()

    if callable(after_speak):
        after_speak()

async def speak_async(text, after_speak=None):
    should_stop.clear()

    wav_path = get_cache_path(text)
    mp3_path = wav_path.replace(".wav", ".mp3")

    if not os.path.exists(wav_path):
        communicate = edge_tts.Communicate(text, voice=VOICE)
        await communicate.save(mp3_path)
        sound = AudioSegment.from_file(mp3_path, format="mp3")
        sound.export(wav_path, format="wav")
        os.remove(mp3_path)

    stop_current_playback()

    thread = threading.Thread(target=play_audio, args=(wav_path, after_speak), daemon=True)
    thread.start()
    # DO NOT join — let it run in the background

def speak(text, after_speak=None):
    asyncio.run(speak_async(text, after_speak))

def stop_speaking():
    should_stop.set()
    stop_current_playback()
    is_currently_speaking.clear()
