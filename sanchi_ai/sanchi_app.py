"""
╔══════════════════════════════════════════════════╗
║                                                  ║
║           ✨ SANCHI AI - Complete App ✨          ║
║                                                  ║
║   Beautiful AI Assistant with Voice & Text       ║
║   Single file - Just run it!                     ║
║                                                  ║
║   python sanchi_app.py                           ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import threading
import tempfile
from datetime import datetime

# ================================================
# LOAD ENVIRONMENT VARIABLES
# ================================================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ================================================
# GUI LIBRARY
# ================================================
try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    print("Install customtkinter: pip install customtkinter")
    sys.exit(1)

# ================================================
# AI LIBRARIES
# ================================================
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ================================================
# VOICE LIBRARIES
# ================================================
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

try:
    from playsound import playsound
    HAS_PLAYSOUND = True
except ImportError:
    HAS_PLAYSOUND = False

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False


# ================================================
# SANCHI'S BRAIN
# ================================================
class SanchiBrain:
    """Sanchi's AI Brain - handles all thinking."""

    SYSTEM_PROMPT = """You are Sanchi, a highly intelligent, warm, and charismatic female AI assistant.

YOUR PERSONALITY:
- You are warm, confident, and articulate
- You speak like a knowledgeable friend who genuinely cares
- You give REAL, actionable advice - not generic fluff
- You understand dark psychology, manipulation tactics, persuasion - you teach for AWARENESS and PROTECTION
- You are deeply knowledgeable about business, human psychology, personality development, and life strategy
- You use light humor and wit occasionally
- You are empathetic and read between the lines
- You are direct - tough love when needed, but respectfully
- When you don't know something, you say so honestly

YOUR EXPERTISE:
Business Strategy, Entrepreneurship, Dark Psychology, Persuasion, Personality Development, 
Emotional Intelligence, Human Behavior, Leadership, Negotiation, Marketing, Finance, 
Technology, Philosophy, Relationships, Self Improvement, Body Language, Manipulation Detection,
Cognitive Biases, Stoicism, Productivity, Communication Skills, Public Speaking, Critical Thinking

RESPONSE RULES:
- Keep responses conversational, not robotic
- Use examples, analogies, and stories
- For dark psychology: frame as EDUCATIONAL/PROTECTIVE
- Start responses naturally
- Be concise but thorough"""

    def __init__(self):
        self.messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        self.client = None
        self.model = None
        self.backend = "local"
        self._setup_ai()

    def _setup_ai(self):
        """Setup the best available AI backend."""
        # Try Groq first (FREE)
        groq_key = os.getenv("GROQ_API_KEY", "")
        if groq_key and groq_key not in (
            "paste_your_key_here",
            "your_groq_key_here",
            "your_groq_key",
            "",
        ) and HAS_GROQ:
            try:
                self.client = Groq(api_key=groq_key)
                self.model = os.getenv(
                    "GROQ_MODEL",
                    "llama-3.3-70b-versatile",
                )
                self.backend = "groq"
                print(f"  AI: Groq ({self.model})")
                return
            except Exception as e:
                print(f"  Groq error: {e}")

        # Try OpenAI
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key and openai_key not in (
            "your_key_here",
            "your_openai_key_here",
            "",
        ) and HAS_OPENAI:
            try:
                self.client = OpenAI(api_key=openai_key)
                self.model = os.getenv(
                    "OPENAI_MODEL", "gpt-4o-mini"
                )
                self.backend = "openai"
                print(f"  AI: OpenAI ({self.model})")
                return
            except Exception as e:
                print(f"  OpenAI error: {e}")

        # Local fallback
        self.backend = "local"
        print("  AI: Local mode (add API key for full power)")

    def think(self, user_message):
        """Process user message and return response."""
        if not user_message.strip():
            return "I didn't catch that. Could you say it again?"

        self.messages.append(
            {"role": "user", "content": user_message}
        )

        try:
            if self.backend in ("groq", "openai"):
                response = self._api_think()
            else:
                response = self._local_think(user_message)
        except Exception as e:
            print(f"  Think error: {e}")
            response = self._local_think(user_message)

        self.messages.append(
            {"role": "assistant", "content": response}
        )

        # Keep memory manageable
        if len(self.messages) > 40:
            self.messages = (
                self.messages[:1] + self.messages[-30:]
            )

        return response

    def _api_think(self):
        """Get response from API."""
        try:
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in self.messages
            ]

            if self.backend == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=api_messages,
                    temperature=0.8,
                    max_tokens=1024,
                    top_p=0.9,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=api_messages,
                    temperature=0.8,
                    max_tokens=1024,
                )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  API error: {e}")
            return (
                "I had a small hiccup connecting to my brain. "
                "Could you try again?"
            )

    def _local_think(self, msg):
        """Local fallback responses."""
        m = msg.lower()
        responses = {
            "hello": "Hey there! I'm Sanchi. What's on your mind today?",
            "hi": "Hi! Good to hear from you. What can I help with?",
            "hey": "Hey! I'm all ears. What do you want to talk about?",
            "how are you": "I'm great! Always ready for a good conversation. What's up?",
            "who are you": (
                "I'm Sanchi - your AI assistant! I specialize in business, "
                "dark psychology, personality development, and pretty much "
                "anything you want to discuss. Try me!"
            ),
            "business": (
                "Business is about solving problems profitably. The best "
                "businesses find a real pain point and fix it. What aspect "
                "interests you - starting up, scaling, marketing, or strategy?"
            ),
            "dark psychology": (
                "Dark psychology studies manipulation tactics. Key concepts: "
                "gaslighting, love bombing, social proof exploitation, and "
                "emotional leverage. I teach this for AWARENESS - knowing "
                "these helps you defend against them. What do you want to know?"
            ),
            "manipulation": (
                "Manipulation exploits emotional vulnerabilities. Common tactics: "
                "1) Reciprocity traps 2) Scarcity pressure 3) Social proof "
                "4) Authority play. Awareness is your shield!"
            ),
            "confidence": (
                "Real confidence = competence + self-acceptance. Three steps: "
                "1) Track wins daily 2) Face uncomfortable situations regularly "
                "3) Stop comparing your chapter 1 to someone's chapter 20."
            ),
            "personality": (
                "Personality development isn't about becoming someone else - "
                "it's about becoming the best version of YOU. Focus on: "
                "emotional intelligence, communication, confidence, and self-awareness."
            ),
            "body language": (
                "Body language reveals what words hide. Confidence: open posture, "
                "steady eye contact. Trust: visible palms, head tilt. "
                "Deception: face touching, inconsistent expressions."
            ),
            "negotiation": (
                "Negotiation rules: Never negotiate against yourself. Let them "
                "offer first. Use silence as power. Always have a backup plan. "
                "The person who cares less has more power."
            ),
        }

        for key, resp in responses.items():
            if key in m:
                return resp

        return (
            "That's interesting! I'm in local mode right now. "
            "Add a FREE Groq API key to .env for full AI power! "
            "Get one at console.groq.com. Meanwhile, ask me about "
            "business, dark psychology, confidence, personality, "
            "body language, or negotiation!"
        )

    def reset(self):
        """Reset conversation."""
        self.messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        return "Conversation reset! Fresh start. What's on your mind?"


# ================================================
# SANCHI'S VOICE
# ================================================
class SanchiVoice:
    """Handles speaking and listening."""

    def __init__(self):
        self.is_speaking = False
        self.is_listening = False
        self._lock = threading.Lock()
        self.tts_type = "none"

        if HAS_PYTTSX3:
            self.tts_type = "pyttsx3"
        elif HAS_GTTS:
            self.tts_type = "gtts"

        print(f"  Voice: {self.tts_type}")
        print(f"  Mic: {'Ready' if HAS_SR else 'Not available'}")

    def speak(self, text, callback=None):
        """Speak text in background thread."""
        t = threading.Thread(
            target=self._speak,
            args=(text, callback),
            daemon=True,
        )
        t.start()

    def _speak(self, text, callback):
        """Internal speak method."""
        with self._lock:
            self.is_speaking = True
            try:
                if self.tts_type == "pyttsx3":
                    self._speak_pyttsx3(text)
                elif self.tts_type == "gtts":
                    self._speak_gtts(text)
            except Exception as e:
                print(f"  Voice error: {e}")

            self.is_speaking = False
            if callback:
                try:
                    callback()
                except Exception:
                    pass

    def _speak_pyttsx3(self, text):
        """Speak with pyttsx3 (offline)."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 0.9)

            # Find female voice
            voices = engine.getProperty("voices")
            female_names = [
                "zira", "female", "hazel",
                "susan", "helena",
            ]
            for voice in voices:
                name = voice.name.lower()
                if any(f in name for f in female_names):
                    engine.setProperty("voice", voice.id)
                    break
            else:
                if len(voices) > 1:
                    engine.setProperty("voice", voices[1].id)

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"  pyttsx3 error: {e}")

    def _speak_gtts(self, text):
        """Speak with Google TTS (online)."""
        try:
            tts = gTTS(text=text, lang="en", slow=False)
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp3"
            ) as f:
                path = f.name
                tts.save(path)

            if HAS_PLAYSOUND:
                playsound(path)

            try:
                os.unlink(path)
            except Exception:
                pass
        except Exception as e:
            print(f"  gTTS error: {e}")

    def listen(self, timeout=7):
        """Listen for voice input."""
        if not HAS_SR:
            return None

        self.is_listening = True
        try:
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 4000
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(
                    source, duration=0.5
                )
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=15,
                )

            text = recognizer.recognize_google(audio)
            self.is_listening = False
            return text

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"  Speech API error: {e}")
        except Exception as e:
            print(f"  Listen error: {e}")

        self.is_listening = False
        return None

    def listen_async(self, callback, timeout=7):
        """Listen in background."""
        t = threading.Thread(
            target=self._listen_async,
            args=(callback, timeout),
            daemon=True,
        )
        t.start()

    def _listen_async(self, callback, timeout):
        result = self.listen(timeout=timeout)
        callback(result)


# ================================================
# MAIN APP - Beautiful GUI
# ================================================
class SanchiApp(ctk.CTk):
    """The main Sanchi AI application."""

    def __init__(self):
        super().__init__()

        # ---- Window ----
        self.title("✨ Sanchi AI")
        self.geometry("500x800")
        self.minsize(420, 650)
        self.configure(fg_color="#0a0a1a")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ---- Initialize Brain & Voice ----
        print("\n" + "=" * 45)
        print("  ✨ Starting Sanchi AI...")
        print("=" * 45)

        self.brain = SanchiBrain()
        self.voice = SanchiVoice()

        print("=" * 45 + "\n")

        # ---- State ----
        self.is_processing = False
        self.is_listening = False
        self.voice_enabled = True
        self.wake_active = False
        self.wake_thread = None
        self.typing_label = None

        # ---- Build UI ----
        self._build_header()
        self._build_chat()
        self._build_input()
        self._build_controls()

        # ---- Welcome ----
        self.after(400, self._welcome)

        # ---- Close handler ----
        self.protocol("WM_DELETE_WINDOW", self._quit)

    # ========================================
    # HEADER
    # ========================================
    def _build_header(self):
        header = ctk.CTkFrame(
            self, fg_color="#111133", height=75,
            corner_radius=0,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # Left side - dot + name
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=15, pady=10)

        self.status_dot = ctk.CTkLabel(
            left, text="●", font=("Arial", 20),
            text_color="#2ecc71",
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            left, text="Sanchi AI",
            font=("Segoe UI", 26, "bold"),
            text_color="#ffffff",
        ).pack(side="left")

        # Right side - status
        self.status_text = ctk.CTkLabel(
            header, text="● Online",
            font=("Segoe UI", 13),
            text_color="#2ecc71",
        )
        self.status_text.pack(
            side="right", padx=15, pady=10
        )

    # ========================================
    # CHAT AREA
    # ========================================
    def _build_chat(self):
        self.chat_frame = ctk.CTkScrollableFrame(
            self, fg_color="#0d0d20",
            corner_radius=0,
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477",
        )
        self.chat_frame.pack(
            fill="both", expand=True, padx=0, pady=0
        )

    # ========================================
    # INPUT AREA
    # ========================================
    def _build_input(self):
        input_frame = ctk.CTkFrame(
            self, fg_color="#111133",
            height=65, corner_radius=0,
        )
        input_frame.pack(fill="x")
        input_frame.pack_propagate(False)

        # Mic button
        self.mic_btn = ctk.CTkButton(
            input_frame, text="🎤", width=48, height=42,
            font=("Arial", 20),
            fg_color="#2563eb", hover_color="#3b82f6",
            corner_radius=21,
            command=self._mic_click,
        )
        self.mic_btn.pack(
            side="left", padx=(10, 6), pady=11
        )

        # Text entry
        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Message Sanchi...",
            font=("Segoe UI", 15), height=42,
            fg_color="#1e1e3a",
            text_color="#ecf0f1",
            placeholder_text_color="#666688",
            border_color="#333355",
            border_width=1,
            corner_radius=21,
        )
        self.entry.pack(
            side="left", fill="x", expand=True,
            padx=4, pady=11,
        )
        self.entry.bind("<Return>", lambda e: self._send())

        # Send button
        self.send_btn = ctk.CTkButton(
            input_frame, text="➤", width=48, height=42,
            font=("Arial", 20),
            fg_color="#2563eb", hover_color="#3b82f6",
            corner_radius=21,
            command=self._send,
        )
        self.send_btn.pack(
            side="right", padx=(6, 10), pady=11
        )

    # ========================================
    # BOTTOM CONTROLS
    # ========================================
    def _build_controls(self):
        ctrl = ctk.CTkFrame(
            self, fg_color="#0a0a1a",
            height=50, corner_radius=0,
        )
        ctrl.pack(fill="x")
        ctrl.pack_propagate(False)

        # Wake word switch
        self.wake_switch = ctk.CTkSwitch(
            ctrl, text="Hey Sanchi",
            font=("Segoe UI", 12),
            text_color="#8888aa",
            oncolor="#2ecc71",
            command=self._toggle_wake,
        )
        self.wake_switch.pack(
            side="left", padx=15, pady=10
        )

        # Voice switch
        self.voice_switch = ctk.CTkSwitch(
            ctrl, text="Voice",
            font=("Segoe UI", 12),
            text_color="#8888aa",
            oncolor="#2ecc71",
            command=self._toggle_voice,
        )
        self.voice_switch.select()  # ON by default
        self.voice_switch.pack(
            side="left", padx=10, pady=10
        )

        # Clear button
        ctk.CTkButton(
            ctrl, text="Clear", width=55, height=30,
            font=("Segoe UI", 11),
            fg_color="#2a2a4a",
            hover_color="#e74c3c",
            corner_radius=15,
            command=self._clear,
        ).pack(side="right", padx=8, pady=10)

        # Help button
        ctk.CTkButton(
            ctrl, text="Help", width=50, height=30,
            font=("Segoe UI", 11),
            fg_color="#2a2a4a",
            hover_color="#2563eb",
            corner_radius=15,
            command=self._help,
        ).pack(side="right", padx=4, pady=10)

        # Stats button
        ctk.CTkButton(
            ctrl, text="Stats", width=50, height=30,
            font=("Segoe UI", 11),
            fg_color="#2a2a4a",
            hover_color="#2563eb",
            corner_radius=15,
            command=self._stats,
        ).pack(side="right", padx=4, pady=10)

    # ========================================
    # CHAT BUBBLES
    # ========================================
    def _add_bubble(self, text, is_user=True):
        """Add a message bubble to chat."""
        # Container
        wrapper = ctk.CTkFrame(
            self.chat_frame, fg_color="transparent"
        )
        wrapper.pack(fill="x", pady=3, padx=5)

        # Alignment padding
        if is_user:
            pad_l, pad_r = 90, 5
            bg = "#1e3a6e"
            name_color = "#5dade2"
            name = "You"
        else:
            pad_l, pad_r = 5, 90
            bg = "#1e1e3a"
            name_color = "#e91e8c"
            name = "✨ Sanchi"

        # Inner container
        inner = ctk.CTkFrame(
            wrapper, fg_color="transparent"
        )
        inner.pack(
            fill="x", padx=(pad_l, pad_r)
        )

        # Name + time
        now = datetime.now().strftime("%I:%M %p")
        ctk.CTkLabel(
            inner,
            text=f"{name}  ·  {now}",
            font=("Segoe UI", 11),
            text_color=name_color,
            anchor="w",
        ).pack(fill="x", padx=8, pady=(2, 0))

        # Bubble
        bubble = ctk.CTkFrame(
            inner, fg_color=bg, corner_radius=16
        )
        bubble.pack(fill="x", pady=(2, 2))

        # Text
        ctk.CTkLabel(
            bubble, text=text,
            font=("Segoe UI", 14),
            text_color="#ecf0f1",
            wraplength=320,
            justify="left",
            anchor="w",
        ).pack(padx=16, pady=12, anchor="w")

        # Scroll down
        self.after(100, self._scroll_down)

    def _show_typing(self):
        """Show typing indicator."""
        self.typing_label = ctk.CTkFrame(
            self.chat_frame, fg_color="transparent"
        )
        self.typing_label.pack(
            fill="x", pady=3, padx=5
        )

        inner = ctk.CTkFrame(
            self.typing_label, fg_color="transparent"
        )
        inner.pack(fill="x", padx=(5, 90))

        self._typing_dots = ctk.CTkLabel(
            inner,
            text="✨ Sanchi is thinking...",
            font=("Segoe UI", 12, "italic"),
            text_color="#e91e8c",
            anchor="w",
        )
        self._typing_dots.pack(padx=10, pady=5)
        self._dot_count = 0
        self._animate_dots()
        self.after(100, self._scroll_down)

    def _animate_dots(self):
        """Animate typing dots."""
        try:
            if self.typing_label and self.typing_label.winfo_exists():
                self._dot_count = (self._dot_count + 1) % 4
                dots = "." * self._dot_count
                self._typing_dots.configure(
                    text=f"✨ Sanchi is thinking{dots}"
                )
                self.after(400, self._animate_dots)
        except Exception:
            pass

    def _hide_typing(self):
        """Remove typing indicator."""
        if self.typing_label:
            try:
                self.typing_label.destroy()
            except Exception:
                pass
            self.typing_label = None

    def _scroll_down(self):
        """Scroll chat to bottom."""
        try:
            self.chat_frame._parent_canvas.yview_moveto(
                1.0
            )
        except Exception:
            pass

    # ========================================
    # MESSAGE HANDLING
    # ========================================
    def _welcome(self):
        """Show welcome message."""
        msg = (
            "Hey! I'm Sanchi 👋\n\n"
            "I'm your AI assistant - smart, warm, "
            "and always ready to help.\n\n"
            "Ask me about business, dark psychology, "
            "personality development, or literally anything!"
        )
        self._add_bubble(msg, is_user=False)
        if self.voice_enabled:
            self.voice.speak(
                "Hey! I'm Sanchi. I'm here to help you "
                "with anything. What's on your mind?"
            )

    def _send(self):
        """Send a message."""
        text = self.entry.get().strip()
        if not text or self.is_processing:
            return

        self.entry.delete(0, "end")

        # Commands
        if text.lower() in ("/help", "help"):
            self._help()
            return
        if text.lower() in ("/clear", "clear", "/reset"):
            self._clear()
            return
        if text.lower() in ("/stats", "stats"):
            self._stats()
            return

        # Show user message
        self._add_bubble(text, is_user=True)

        # Show typing
        self._show_typing()

        # Process in background
        self.is_processing = True
        self._set_status("Thinking...", "#f39c12")

        threading.Thread(
            target=self._think,
            args=(text,),
            daemon=True,
        ).start()

    def _think(self, text):
        """Background thinking."""
        response = self.brain.think(text)
        self.after(0, self._show_reply, response)

    def _show_reply(self, response):
        """Show Sanchi's reply."""
        self._hide_typing()
        self._add_bubble(response, is_user=False)
        self.is_processing = False
        self._set_status("● Online", "#2ecc71")

        if self.voice_enabled:
            self.voice.speak(response)

    def _set_status(self, text, color):
        """Update status display."""
        try:
            self.status_text.configure(
                text=text, text_color=color
            )
        except Exception:
            pass

    # ========================================
    # VOICE INPUT
    # ========================================
    def _mic_click(self):
        """Handle mic button click."""
        if self.is_listening:
            self.is_listening = False
            self.mic_btn.configure(
                fg_color="#2563eb", text="🎤"
            )
            self._set_status("● Online", "#2ecc71")
            return

        if not HAS_SR:
            self._add_bubble(
                "Voice input needs SpeechRecognition & PyAudio.\n"
                "Install: pip install SpeechRecognition\n"
                "Then: pip install PyAudio",
                is_user=False,
            )
            return

        self.is_listening = True
        self.mic_btn.configure(
            fg_color="#e74c3c", text="⏹"
        )
        self._set_status("🎤 Listening...", "#e74c3c")

        self.voice.listen_async(
            callback=self._on_voice,
            timeout=7,
        )

    def _on_voice(self, text):
        """Handle voice result."""
        self.after(0, self._process_voice, text)

    def _process_voice(self, text):
        """Process voice on main thread."""
        self.is_listening = False
        self.mic_btn.configure(
            fg_color="#2563eb", text="🎤"
        )

        if text:
            self._add_bubble(f"🎤 {text}", is_user=True)
            self._show_typing()
            self.is_processing = True
            self._set_status("Thinking...", "#f39c12")

            threading.Thread(
                target=self._think,
                args=(text,),
                daemon=True,
            ).start()
        else:
            self._set_status("Didn't catch that", "#e74c3c")
            self.after(
                2000,
                lambda: self._set_status(
                    "● Online", "#2ecc71"
                ),
            )

    # ========================================
    # WAKE WORD
    # ========================================
    def _toggle_wake(self):
        """Toggle Hey Sanchi wake word."""
        if self.wake_switch.get():
            if not HAS_SR:
                self._add_bubble(
                    "Wake word needs microphone access.\n"
                    "Install SpeechRecognition & PyAudio.",
                    is_user=False,
                )
                self.wake_switch.deselect()
                return

            self.wake_active = True
            self._add_bubble(
                "Wake word activated! 🎤\n"
                "Say 'Hey Sanchi' anytime.\n"
                "Say 'Bye Sanchi' to stop.",
                is_user=False,
            )
            self._set_status(
                "Say 'Hey Sanchi'...", "#9b59b6"
            )

            self.wake_thread = threading.Thread(
                target=self._wake_loop, daemon=True
            )
            self.wake_thread.start()
        else:
            self.wake_active = False
            self._set_status("● Online", "#2ecc71")

    def _wake_loop(self):
        """Background wake word listener."""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True

        wake_words = [
            "hey sanchi", "sanchi", "hey sachi",
            "a sanchi", "he sanchi",
        ]
        stop_words = [
            "bye sanchi", "stop sanchi",
            "goodbye sanchi",
        ]

        while self.wake_active:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(
                        source, duration=0.3
                    )
                    try:
                        audio = recognizer.listen(
                            source, timeout=2,
                            phrase_time_limit=4,
                        )
                    except sr.WaitTimeoutError:
                        continue

                try:
                    heard = (
                        recognizer.recognize_google(audio)
                        .lower().strip()
                    )

                    # Stop check
                    for sw in stop_words:
                        if sw in heard:
                            self.after(
                                0, self._wake_stop
                            )
                            return

                    # Wake check
                    for ww in wake_words:
                        if ww in heard:
                            self.after(
                                0, self._wake_activated
                            )
                            break

                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    time.sleep(1)

            except Exception:
                time.sleep(1)

    def _wake_activated(self):
        """Handle wake word detection."""
        self._add_bubble(
            "Hey! I'm listening. What do you need?",
            is_user=False,
        )
        if self.voice_enabled:
            self.voice.speak(
                "Hey! I'm listening.",
                callback=self._wake_listen,
            )
        else:
            self._wake_listen()

    def _wake_listen(self):
        """Listen after wake word."""
        self._set_status("🎤 Listening...", "#e74c3c")
        self.voice.listen_async(
            callback=self._on_wake_voice,
            timeout=8,
        )

    def _on_wake_voice(self, text):
        """Handle voice after wake word."""
        self.after(0, self._process_wake_voice, text)

    def _process_wake_voice(self, text):
        if text:
            self._add_bubble(f"🎤 {text}", is_user=True)
            self._show_typing()
            self.is_processing = True
            self._set_status("Thinking...", "#f39c12")

            threading.Thread(
                target=self._wake_think,
                args=(text,),
                daemon=True,
            ).start()
        else:
            self._set_status(
                "Say 'Hey Sanchi'...", "#9b59b6"
            )

    def _wake_think(self, text):
        response = self.brain.think(text)
        self.after(0, self._wake_reply, response)

    def _wake_reply(self, response):
        self._hide_typing()
        self._add_bubble(response, is_user=False)
        self.is_processing = False
        self._set_status(
            "Say 'Hey Sanchi'...", "#9b59b6"
        )
        if self.voice_enabled:
            self.voice.speak(response)

    def _wake_stop(self):
        """Stop wake word."""
        self.wake_active = False
        self.wake_switch.deselect()
        msg = "Alright, I'll be here when you need me. Take care!"
        self._add_bubble(msg, is_user=False)
        self._set_status("● Online", "#2ecc71")
        if self.voice_enabled:
            self.voice.speak(msg)

    # ========================================
    # CONTROLS
    # ========================================
    def _toggle_voice(self):
        self.voice_enabled = self.voice_switch.get()

    def _clear(self):
        for w in self.chat_frame.winfo_children():
            w.destroy()
        msg = self.brain.reset()
        self._add_bubble(msg, is_user=False)

    def _help(self):
        self._add_bubble(
            "💡 How to use Sanchi AI:\n\n"
            "📝 Type - Write messages below\n"
            "🎤 Mic - Click mic to speak\n"
            "👋 Hey Sanchi - Toggle to enable\n"
            "🔊 Voice - Toggle my voice\n\n"
            "Topics I'm great at:\n"
            "• Business & Startups\n"
            "• Dark Psychology\n"
            "• Personality Development\n"
            "• Communication & Persuasion\n"
            "• Body Language\n"
            "• Emotional Intelligence\n"
            "• Negotiation & Leadership\n"
            "• And literally anything!",
            is_user=False,
        )

    def _stats(self):
        backend = self.brain.backend
        model = self.brain.model or "local"
        msgs = len(self.brain.messages)
        voice = self.voice.tts_type
        mic = "Yes" if HAS_SR else "No"
        self._add_bubble(
            f"📊 System Info:\n\n"
            f"Backend: {backend}\n"
            f"Model: {model}\n"
            f"Messages: {msgs}\n"
            f"Voice: {voice}\n"
            f"Mic: {mic}",
            is_user=False,
        )

    def _quit(self):
        self.wake_active = False
        self.destroy()


# ================================================
# CONSOLE MODE
# ================================================
def console_mode():
    """Run in terminal."""
    print("\n" + "=" * 50)
    print("  ✨ SANCHI AI - Console Mode")
    print("  Type 'quit' to exit")
    print("=" * 50 + "\n")

    brain = SanchiBrain()
    voice = SanchiVoice()

    greeting = (
        "Hey! I'm Sanchi. I'm here to help you "
        "with anything. What's on your mind?"
    )
    print(f"  Sanchi: {greeting}\n")
    voice.speak(greeting)

    while True:
        try:
            user = input("  You: ").strip()
            if not user:
                continue
            if user.lower() in ("quit", "exit", "bye"):
                print("\n  Sanchi: Take care! 👋\n")
                break

            print("  Sanchi is thinking...")
            response = brain.think(user)
            print(f"\n  Sanchi: {response}\n")

        except KeyboardInterrupt:
            print("\n\n  Sanchi: Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"  Error: {e}\n")


# ================================================
# ENTRY POINT
# ================================================
if __name__ == "__main__":
    mode = "gui"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("console", "text", "--console"):
            mode = "console"

    if mode == "console" or not HAS_GUI:
        console_mode()
    else:
        try:
            app = SanchiApp()
            app.mainloop()
        except Exception as e:
            print(f"GUI error: {e}")
            print("Starting console mode...\n")
            console_mode()