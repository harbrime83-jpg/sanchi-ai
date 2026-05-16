"""
Sanchi's Voice Engine
Handles speech-to-text (listening) and text-to-speech (speaking).
"""

import os
import threading
import tempfile
from typing import Optional, Callable

# Text-to-Speech
try:
    import pyttsx3

    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    from gtts import gTTS

    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

# Speech-to-Text
try:
    import speech_recognition as sr

    HAS_SR = True
except ImportError:
    HAS_SR = False

# Audio playback
try:
    from playsound import playsound

    HAS_PLAYSOUND = True
except ImportError:
    HAS_PLAYSOUND = False


class VoiceEngine:
    """
    Handles all voice I/O for Sanchi.
    - Speech-to-Text: Converts user's voice to text
    - Text-to-Speech: Converts Sanchi's text to natural speech
    """

    def __init__(self, tts_engine: str = "auto", voice_speed: int = 175):
        self.tts_engine_type = self._select_tts(tts_engine)
        self.voice_speed = voice_speed
        self.is_listening = False
        self.is_speaking = False
        self._lock = threading.Lock()

        # Initialize TTS
        self.tts = None
        if self.tts_engine_type == "pyttsx3" and HAS_PYTTSX3:
            self._init_pyttsx3()

        # Initialize STT
        self.recognizer = None
        self.microphone = None
        if HAS_SR:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8

        print(f"[Voice Engine] TTS: {self.tts_engine_type}")
        print(f"[Voice Engine] STT: {'Available' if HAS_SR else 'Not Available'}")

    def _select_tts(self, preferred: str) -> str:
        """Select the best TTS engine."""
        if preferred != "auto":
            return preferred
        if HAS_PYTTSX3:
            return "pyttsx3"
        elif HAS_GTTS:
            return "gtts"
        return "none"

    def _init_pyttsx3(self):
        """Initialize pyttsx3 with female voice."""
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", self.voice_speed)
            self.tts.setProperty("volume", 0.9)

            # Try to set a female voice
            voices = self.tts.getProperty("voices")
            female_voice_set = False
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    self.tts.setProperty("voice", voice.id)
                    female_voice_set = True
                    print(f"[Voice Engine] Selected voice: {voice.name}")
                    break

            if not female_voice_set and len(voices) > 1:
                # Usually index 1 is female on Windows
                self.tts.setProperty("voice", voices[1].id)
                print(f"[Voice Engine] Selected voice: {voices[1].name}")

        except Exception as e:
            print(f"[Voice Engine] pyttsx3 init error: {e}")
            self.tts = None

    def speak(self, text: str, callback: Optional[Callable] = None):
        """
        Convert text to speech and play it.
        Runs in a separate thread to not block the UI.
        """
        thread = threading.Thread(target=self._speak_thread, args=(text, callback))
        thread.daemon = True
        thread.start()

    def _speak_thread(self, text: str, callback: Optional[Callable]):
        """Internal method for speaking in a thread."""
        with self._lock:
            self.is_speaking = True

            try:
                if self.tts_engine_type == "pyttsx3" and self.tts:
                    self._speak_pyttsx3(text)
                elif self.tts_engine_type == "gtts" and HAS_GTTS:
                    self._speak_gtts(text)
                else:
                    print(f"[Sanchi says]: {text}")
            except Exception as e:
                print(f"[Voice Engine] Speech error: {e}")
                print(f"[Sanchi says]: {text}")

            self.is_speaking = False

            if callback:
                callback()

    def _speak_pyttsx3(self, text: str):
        """Speak using pyttsx3 (offline)."""
        try:
            # Reinitialize engine for thread safety
            engine = pyttsx3.init()
            engine.setProperty("rate", self.voice_speed)
            engine.setProperty("volume", 0.9)

            voices = engine.getProperty("voices")
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break
            else:
                if len(voices) > 1:
                    engine.setProperty("voice", voices[1].id)

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[Voice Engine] pyttsx3 error: {e}")

    def _speak_gtts(self, text: str):
        """Speak using Google TTS (online, better quality)."""
        try:
            tts = gTTS(text=text, lang="en", slow=False, tld="co.in")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_file = fp.name
                tts.save(temp_file)

            if HAS_PLAYSOUND:
                playsound(temp_file)

            os.unlink(temp_file)
        except Exception as e:
            print(f"[Voice Engine] gTTS error: {e}")

    def listen(self, timeout: int = 5, phrase_limit: int = 15) -> Optional[str]:
        """
        Listen for user's voice and convert to text.
        Returns the recognized text or None.
        """
        if not HAS_SR:
            print("[Voice Engine] Speech recognition not available")
            return None

        self.is_listening = True

        try:
            with sr.Microphone() as source:
                print("[Sanchi] Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )

            print("[Sanchi] Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"[User said]: {text}")
            self.is_listening = False
            return text

        except sr.WaitTimeoutError:
            print("[Voice Engine] Listening timed out")
        except sr.UnknownValueError:
            print("[Voice Engine] Could not understand audio")
        except sr.RequestError as e:
            print(f"[Voice Engine] API error: {e}")
        except Exception as e:
            print(f"[Voice Engine] Error: {e}")

        self.is_listening = False
        return None

    def listen_async(
        self, callback: Callable, timeout: int = 5, phrase_limit: int = 15
    ):
        """Listen asynchronously and call callback with result."""
        thread = threading.Thread(
            target=self._listen_thread, args=(callback, timeout, phrase_limit)
        )
        thread.daemon = True
        thread.start()

    def _listen_thread(self, callback: Callable, timeout: int, phrase_limit: int):
        """Internal async listen thread."""
        result = self.listen(timeout=timeout, phrase_limit=phrase_limit)
        callback(result)

    def is_available(self) -> dict:
        """Check which voice features are available."""
        return {
            "tts": self.tts_engine_type != "none",
            "tts_engine": self.tts_engine_type,
            "stt": HAS_SR,
            "microphone": self._check_microphone(),
        }

    def _check_microphone(self) -> bool:
        """Check if microphone is available."""
        if not HAS_SR:
            return False
        try:
            mics = sr.Microphone.list_microphone_names()
            return len(mics) > 0
        except:
            return False
