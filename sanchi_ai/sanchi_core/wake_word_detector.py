"""
Wake Word Detector for "Hey Sanchi"
"""

import threading
import time
from typing import Callable, Optional

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False


class WakeWordDetector:
    """Continuously listens for 'Hey Sanchi' wake word."""

    WAKE_WORDS = [
        "hey sanchi",
        "hey sachi",
        "hey sanchy",
        "hey sanshee",
        "a sanchi",
        "hey sunchi",
        "sanchi",
        "hey saanchi",
        "hay sanchi",
    ]

    STOP_WORDS = [
        "stop sanchi",
        "bye sanchi",
        "goodbye sanchi",
        "sleep sanchi",
        "stop listening",
    ]

    def __init__(
        self, on_wake: Callable, on_stop: Optional[Callable] = None
    ):
        self.on_wake = on_wake
        self.on_stop = on_stop
        self.is_running = False
        self.is_paused = False
        self._thread = None
        self._lock = threading.Lock()

        if HAS_SR:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 3000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.6
        else:
            self.recognizer = None

    def start(self):
        if not HAS_SR:
            print("[Wake Word] Speech recognition not available")
            return

        self.is_running = True
        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True
        )
        self._thread.start()
        print(
            "[Wake Word] Detector started - Say 'Hey Sanchi' to activate"
        )

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=3)
        print("[Wake Word] Detector stopped")

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def _listen_loop(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(0.3)
                continue

            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(
                        source, duration=0.3
                    )
                    try:
                        audio = self.recognizer.listen(
                            source, timeout=2, phrase_time_limit=4
                        )
                    except sr.WaitTimeoutError:
                        continue

                try:
                    text = (
                        self.recognizer.recognize_google(audio)
                        .lower()
                        .strip()
                    )
                    print(f"[Wake Word] Heard: '{text}'")

                    for stop_word in self.STOP_WORDS:
                        if stop_word in text:
                            print("[Wake Word] Stop command detected")
                            if self.on_stop:
                                self.on_stop()
                            return

                    for wake_word in self.WAKE_WORDS:
                        if wake_word in text:
                            print("[Wake Word] *** ACTIVATED ***")
                            self.pause()
                            self.on_wake()
                            break

                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    time.sleep(1)

            except Exception as e:
                print(f"[Wake Word] Error: {e}")
                time.sleep(1)


class KeyboardWakeDetector:
    """Fallback: keyboard-based wake word for systems without mic."""

    def __init__(self, on_wake: Callable):
        self.on_wake = on_wake
        self.is_running = False
        self._thread = None

    def start(self):
        self.is_running = True
        self._thread = threading.Thread(
            target=self._input_loop, daemon=True
        )
        self._thread.start()
        print(
            "[Keyboard Wake] Type 'hey sanchi' or press Enter to activate"
        )

    def stop(self):
        self.is_running = False

    def _input_loop(self):
        while self.is_running:
            try:
                user_input = input().strip().lower()
                if user_input in ("hey sanchi", "sanchi", ""):
                    self.on_wake()
                elif user_input in ("quit", "exit", "bye"):
                    self.is_running = False
                    break
            except EOFError:
                break