"""
==============================================
  SANCHI AI - Main Application
  Your Intelligent Female AI Assistant

  Built with CustomTkinter (Modern Dark UI)

  Run GUI:     python main.py
  Run Console: python main.py --mode console
==============================================
"""

import os
import sys
import threading
import time

# ============================================
# Import Sanchi core modules (these DON'T change)
# ============================================
from sanchi_core.brain import SanchiBrain
from sanchi_core.voice_engine import VoiceEngine
from sanchi_core.personality import SanchiPersonality
from sanchi_core.wake_word_detector import WakeWordDetector

# ============================================
# Try importing CustomTkinter
# ============================================
try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    print("[Warning] customtkinter not installed.")
    print("Install it: pip install customtkinter")


# ================================================
# GUI MODE - CustomTkinter Window
# ================================================
if HAS_CTK:
    from ui.chat_screen import ChatScrollFrame, TypingIndicator

    class SanchiGUI(ctk.CTk):
        """
        Main Sanchi AI GUI Application.
        Beautiful dark-themed chat interface.
        """

        def __init__(self):
            super().__init__()

            # ---- Window Setup ----
            self.title("Sanchi AI - Your Intelligent Assistant")
            self.geometry("480x780")
            self.minsize(400, 600)
            self.configure(fg_color="#0d0d1a")

            # Set dark theme
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")

            # ---- Initialize AI Components ----
            print("\n" + "=" * 50)
            print("   Initializing Sanchi AI...")
            print("=" * 50)

            self.brain = SanchiBrain(backend="auto")
            self.voice = VoiceEngine()
            self.wake_detector = None
            self._is_processing = False
            self._is_listening = False
            self._voice_output = True
            self._typing_indicator = None

            # Print system info
            stats = self.brain.get_stats()
            voice_info = self.voice.is_available()
            print(f"\n  AI Backend : {stats['backend']}")
            print(f"  AI Model   : {stats['model']}")
            print(f"  TTS Engine : {voice_info['tts_engine']}")
            print(f"  STT Ready  : {voice_info['stt']}")
            print(f"  Microphone : {voice_info['microphone']}")
            print("=" * 50 + "\n")

            # ---- Build the UI ----
            self._build_ui()

            # ---- Show Welcome Message ----
            self.after(500, self._show_welcome)

            # ---- Handle window close ----
            self.protocol("WM_DELETE_WINDOW", self._on_close)

        def _build_ui(self):
            """Build the entire user interface."""

            # =====================
            # TOP HEADER BAR
            # =====================
            header_frame = ctk.CTkFrame(
                self,
                fg_color="#16213e",
                height=70,
                corner_radius=0,
            )
            header_frame.pack(fill="x", side="top")
            header_frame.pack_propagate(False)

            # Status dot (green = active)
            self.status_dot = ctk.CTkLabel(
                header_frame,
                text="●",
                font=("Arial", 18),
                text_color="#2ecc71",
            )
            self.status_dot.pack(
                side="left", padx=(15, 5), pady=10
            )

            # Title
            title_label = ctk.CTkLabel(
                header_frame,
                text="Sanchi AI",
                font=("Segoe UI", 24, "bold"),
                text_color="#ffffff",
            )
            title_label.pack(side="left", padx=5, pady=10)

            # Status text (right side)
            self.status_label = ctk.CTkLabel(
                header_frame,
                text="Ready",
                font=("Segoe UI", 12),
                text_color="#5dade2",
            )
            self.status_label.pack(
                side="right", padx=15, pady=10
            )

            # =====================
            # CHAT MESSAGE AREA
            # =====================
            self.chat_frame = ChatScrollFrame(
                self,
                fg_color="#1a1a2e",
                corner_radius=0,
            )
            self.chat_frame.pack(
                fill="both",
                expand=True,
                padx=0,
                pady=0,
            )

            # =====================
            # INPUT AREA
            # =====================
            input_frame = ctk.CTkFrame(
                self,
                fg_color="#16213e",
                height=60,
                corner_radius=0,
            )
            input_frame.pack(fill="x", side="bottom")
            input_frame.pack_propagate(False)

            # Microphone button
            self.mic_button = ctk.CTkButton(
                input_frame,
                text="🎤",
                width=45,
                height=40,
                font=("Arial", 18),
                fg_color="#2980b9",
                hover_color="#3498db",
                corner_radius=20,
                command=self._toggle_voice_input,
            )
            self.mic_button.pack(
                side="left", padx=(10, 5), pady=10
            )

            # Text input field
            self.text_input = ctk.CTkEntry(
                input_frame,
                placeholder_text="Type a message to Sanchi...",
                font=("Segoe UI", 14),
                height=40,
                fg_color="#2c3e50",
                text_color="#ecf0f1",
                placeholder_text_color="#7f8c8d",
                border_color="#34495e",
                corner_radius=20,
            )
            self.text_input.pack(
                side="left",
                fill="x",
                expand=True,
                padx=5,
                pady=10,
            )
            # Bind Enter key to send
            self.text_input.bind(
                "<Return>", lambda e: self._send_message()
            )

            # Send button
            self.send_button = ctk.CTkButton(
                input_frame,
                text="➤",
                width=45,
                height=40,
                font=("Arial", 18),
                fg_color="#2980b9",
                hover_color="#3498db",
                corner_radius=20,
                command=self._send_message,
            )
            self.send_button.pack(
                side="right", padx=(5, 10), pady=10
            )

            # =====================
            # BOTTOM CONTROL BAR
            # =====================
            control_frame = ctk.CTkFrame(
                self,
                fg_color="#0d0d1a",
                height=45,
                corner_radius=0,
            )
            control_frame.pack(fill="x", side="bottom")
            control_frame.pack_propagate(False)

            # Wake Word Toggle
            self.wake_var = ctk.BooleanVar(value=False)
            self.wake_toggle = ctk.CTkSwitch(
                control_frame,
                text="Hey Sanchi",
                font=("Segoe UI", 12),
                text_color="#bdc3c7",
                variable=self.wake_var,
                command=self._toggle_wake_word,
                oncolor="#2ecc71",
                offcolor="#7f8c8d",
                progress_color="#27ae60",
            )
            self.wake_toggle.pack(
                side="left", padx=15, pady=8
            )

            # Voice Output Toggle
            self.voice_var = ctk.BooleanVar(value=True)
            self.voice_toggle = ctk.CTkSwitch(
                control_frame,
                text="Voice",
                font=("Segoe UI", 12),
                text_color="#bdc3c7",
                variable=self.voice_var,
                command=self._toggle_voice_output,
                oncolor="#2ecc71",
                offcolor="#7f8c8d",
                progress_color="#27ae60",
            )
            self.voice_toggle.pack(
                side="left", padx=15, pady=8
            )

            # Clear Chat Button
            clear_btn = ctk.CTkButton(
                control_frame,
                text="Clear",
                width=60,
                height=28,
                font=("Segoe UI", 11),
                fg_color="#34495e",
                hover_color="#e74c3c",
                corner_radius=14,
                command=self._clear_chat,
            )
            clear_btn.pack(side="right", padx=15, pady=8)

            # Help Button
            help_btn = ctk.CTkButton(
                control_frame,
                text="Help",
                width=50,
                height=28,
                font=("Segoe UI", 11),
                fg_color="#34495e",
                hover_color="#2980b9",
                corner_radius=14,
                command=self._show_help,
            )
            help_btn.pack(side="right", padx=5, pady=8)

        # =====================
        # MESSAGE HANDLING
        # =====================

        def _show_welcome(self):
            """Show Sanchi's welcome greeting."""
            greeting = SanchiPersonality.get_greeting()
            self.chat_frame.add_message(
                greeting, is_user=False
            )
            if self._voice_output:
                self.voice.speak(greeting)

        def _send_message(self):
            """Handle sending a message."""
            message = self.text_input.get().strip()

            if not message or self._is_processing:
                return

            # Clear input
            self.text_input.delete(0, "end")

            # Check for commands
            if self._handle_commands(message):
                return

            # Show user message
            self.chat_frame.add_message(message, is_user=True)

            # Show typing indicator
            self._typing_indicator = (
                self.chat_frame.add_typing_indicator()
            )

            # Process in background
            self._is_processing = True
            self._update_status("Thinking...")
            self.brain.set_verbal_mode(False)

            thread = threading.Thread(
                target=self._process_message,
                args=(message,),
                daemon=True,
            )
            thread.start()

        def _process_message(self, message):
            """Process message in background thread."""
            response = self.brain.think(message)
            # Update UI on main thread
            self.after(0, self._show_response, response)

        def _show_response(self, response):
            """Display Sanchi's response."""
            # Remove typing indicator
            if self._typing_indicator:
                self._typing_indicator.destroy()
                self._typing_indicator = None

            # Show response
            self.chat_frame.add_message(
                response, is_user=False
            )
            self._is_processing = False
            self._update_status("Ready")

            # Speak response
            if self._voice_output:
                self.voice.speak(response)

        def _update_status(self, text):
            """Update the status label."""
            try:
                self.status_label.configure(text=text)
            except Exception:
                pass

        # =====================
        # VOICE INPUT
        # =====================

        def _toggle_voice_input(self):
            """Toggle microphone listening."""
            if self._is_listening:
                self._is_listening = False
                self.mic_button.configure(
                    fg_color="#2980b9", text="🎤"
                )
                self._update_status("Ready")
                return

            # Check if voice input is available
            voice_info = self.voice.is_available()
            if not voice_info["stt"]:
                self.chat_frame.add_message(
                    "Voice input not available. "
                    "Install SpeechRecognition and PyAudio:\n"
                    "pip install SpeechRecognition\n"
                    "pip install PyAudio",
                    is_user=False,
                )
                return

            if not voice_info["microphone"]:
                self.chat_frame.add_message(
                    "No microphone detected! "
                    "Please connect a microphone and try again.",
                    is_user=False,
                )
                return

            # Start listening
            self._is_listening = True
            self.mic_button.configure(
                fg_color="#e74c3c", text="⏹"
            )
            self._update_status("🎤 Listening...")

            self.voice.listen_async(
                callback=self._on_voice_result,
                timeout=7,
            )

        def _on_voice_result(self, text):
            """Handle voice recognition result."""
            self.after(0, self._process_voice_result, text)

        def _process_voice_result(self, text):
            """Process voice result on main thread."""
            self._is_listening = False
            self.mic_button.configure(
                fg_color="#2980b9", text="🎤"
            )

            if text:
                # Show what user said
                self.chat_frame.add_message(
                    f"🎤 {text}", is_user=True
                )

                # Show typing indicator
                self._typing_indicator = (
                    self.chat_frame.add_typing_indicator()
                )

                # Process
                self._is_processing = True
                self._update_status("Thinking...")
                self.brain.set_verbal_mode(True)

                thread = threading.Thread(
                    target=self._process_message,
                    args=(text,),
                    daemon=True,
                )
                thread.start()
            else:
                self._update_status("Didn't catch that")
                self.after(
                    2000,
                    lambda: self._update_status("Ready"),
                )

        # =====================
        # WAKE WORD ("Hey Sanchi")
        # =====================

        def _toggle_wake_word(self):
            """Toggle Hey Sanchi wake word detection."""
            if self.wake_var.get():
                # Turn ON
                voice_info = self.voice.is_available()
                if not voice_info["stt"] or not voice_info["microphone"]:
                    self.chat_frame.add_message(
                        "Wake word needs a microphone. "
                        "Please install PyAudio and connect a mic.",
                        is_user=False,
                    )
                    self.wake_var.set(False)
                    return

                self.wake_detector = WakeWordDetector(
                    on_wake=self._on_wake_word,
                    on_stop=self._on_stop_word,
                )
                self.wake_detector.start()
                self._update_status("Say 'Hey Sanchi'...")
                self.chat_frame.add_message(
                    "Wake word activated! 🎤\n"
                    "Say 'Hey Sanchi' anytime to talk to me.\n"
                    "Say 'Bye Sanchi' to deactivate.",
                    is_user=False,
                )
            else:
                # Turn OFF
                if self.wake_detector:
                    self.wake_detector.stop()
                    self.wake_detector = None
                self._update_status("Ready")

        def _on_wake_word(self):
            """Called when 'Hey Sanchi' is detected."""
            self.after(0, self._handle_wake)

        def _handle_wake(self):
            """Handle wake word activation."""
            wake_response = SanchiPersonality.get_wake_response()
            self.chat_frame.add_message(
                wake_response, is_user=False
            )

            if self._voice_output:
                self.voice.speak(
                    wake_response,
                    callback=self._listen_after_wake,
                )
            else:
                self._listen_after_wake()

        def _listen_after_wake(self):
            """Start listening after wake word response."""
            self._is_listening = True
            self.after(
                0,
                lambda: self._update_status("🎤 Listening..."),
            )
            self.after(
                0,
                lambda: self.mic_button.configure(
                    fg_color="#e74c3c", text="⏹"
                ),
            )
            self.voice.listen_async(
                callback=self._on_wake_voice_result,
                timeout=8,
                phrase_limit=20,
            )

        def _on_wake_voice_result(self, text):
            """Handle voice after wake word."""
            self.after(
                0, self._process_wake_voice, text
            )

        def _process_wake_voice(self, text):
            """Process wake voice result."""
            self._is_listening = False
            self.mic_button.configure(
                fg_color="#2980b9", text="🎤"
            )

            if text:
                self.chat_frame.add_message(
                    f"🎤 {text}", is_user=True
                )
                self._typing_indicator = (
                    self.chat_frame.add_typing_indicator()
                )
                self.brain.set_verbal_mode(True)
                self._is_processing = True
                self._update_status("Thinking...")

                thread = threading.Thread(
                    target=self._process_wake_think,
                    args=(text,),
                    daemon=True,
                )
                thread.start()
            else:
                self._update_status("Say 'Hey Sanchi'...")
                if self.wake_detector:
                    self.wake_detector.resume()

        def _process_wake_think(self, text):
            """Think and respond for wake word interaction."""
            response = self.brain.think(text)
            self.after(
                0, self._show_wake_response, response
            )

        def _show_wake_response(self, response):
            """Show response and resume wake detection."""
            if self._typing_indicator:
                self._typing_indicator.destroy()
                self._typing_indicator = None

            self.chat_frame.add_message(
                response, is_user=False
            )
            self._is_processing = False
            self._update_status("Say 'Hey Sanchi'...")

            if self._voice_output:
                self.voice.speak(
                    response,
                    callback=lambda: (
                        self.wake_detector.resume()
                        if self.wake_detector
                        else None
                    ),
                )
            else:
                if self.wake_detector:
                    self.wake_detector.resume()

        def _on_stop_word(self):
            """Handle 'Bye Sanchi' command."""
            self.after(0, self._handle_stop)

        def _handle_stop(self):
            """Process stop command."""
            farewell = SanchiPersonality.get_farewell()
            self.chat_frame.add_message(
                farewell, is_user=False
            )
            if self._voice_output:
                self.voice.speak(farewell)
            self.wake_var.set(False)
            if self.wake_detector:
                self.wake_detector.stop()
                self.wake_detector = None
            self._update_status("Ready")

        # =====================
        # CONTROLS
        # =====================

        def _toggle_voice_output(self):
            """Toggle Sanchi's voice on/off."""
            self._voice_output = self.voice_var.get()

        def _clear_chat(self):
            """Clear all messages and reset."""
            self.chat_frame.clear_all()
            response = self.brain.reset_conversation()
            self.chat_frame.add_message(
                response, is_user=False
            )

        def _show_help(self):
            """Show help information."""
            help_text = (
                "💡 How to use Sanchi AI:\n\n"
                "📝 Type - Write messages below\n"
                "🎤 Mic - Click mic button to speak\n"
                "👋 Hey Sanchi - Toggle switch to enable\n"
                "🔊 Voice - Toggle Sanchi's voice\n\n"
                "Topics I'm great at:\n"
                "• Business & Startups\n"
                "• Dark Psychology\n"
                "• Personality Development\n"
                "• Communication & Persuasion\n"
                "• Body Language\n"
                "• Emotional Intelligence\n"
                "• Negotiation & Leadership\n"
                "• And much more!"
            )
            self.chat_frame.add_message(
                help_text, is_user=False
            )

        def _handle_commands(self, message):
            """Handle special commands."""
            cmd = message.lower().strip()

            if cmd in ("/help", "help"):
                self._show_help()
                return True

            elif cmd in ("/clear", "/reset", "clear"):
                self._clear_chat()
                return True

            elif cmd in ("/stats", "stats"):
                stats = self.brain.get_stats()
                voice = self.voice.is_available()
                info = (
                    f"📊 System Info:\n\n"
                    f"Backend: {stats['backend']}\n"
                    f"Model: {stats['model']}\n"
                    f"Messages: {stats['messages']}\n"
                    f"TTS: {voice['tts_engine']}\n"
                    f"STT: {'✅' if voice['stt'] else '❌'}\n"
                    f"Mic: {'✅' if voice['microphone'] else '❌'}"
                )
                self.chat_frame.add_message(
                    info, is_user=False
                )
                return True

            return False

        def _on_close(self):
            """Handle window close."""
            if self.wake_detector:
                self.wake_detector.stop()
            print("\n[Sanchi] Goodbye! 👋\n")
            self.destroy()


# ================================================
# CONSOLE MODE (No GUI - Terminal Only)
# ================================================
def run_console_mode():
    """Run Sanchi in the terminal without any GUI."""

    print("\n" + "=" * 55)
    print("  ╔═══════════════════════════════════╗")
    print("  ║      SANCHI AI - Console Mode      ║")
    print("  ╚═══════════════════════════════════╝")
    print("=" * 55)
    print("  Type your message and press Enter.")
    print("  Type 'voice' to switch to voice input.")
    print("  Type 'help' for commands.")
    print("  Type 'quit' to exit.")
    print("=" * 55 + "\n")

    # Initialize
    brain = SanchiBrain(backend="auto")
    voice = VoiceEngine()

    # Print system info
    stats = brain.get_stats()
    voice_info = voice.is_available()
    print(f"  Backend: {stats['backend']} ({stats['model']})")
    print(f"  Voice: {voice_info['tts_engine']}")
    print(
        f"  Mic: {'Ready' if voice_info['microphone'] else 'Not found'}"
    )
    print()

    # Greeting
    greeting = SanchiPersonality.get_greeting()
    print(f"  Sanchi: {greeting}\n")

    if voice_info["tts"]:
        voice.speak(greeting)

    voice_mode = False

    while True:
        try:
            if voice_mode:
                print("  🎤 [Listening... speak now]")
                user_input = voice.listen(timeout=8)
                if not user_input:
                    print(
                        "  [Didn't catch that. "
                        "Type 'text' to switch.]"
                    )
                    fallback = input("  You: ").strip()
                    if fallback.lower() == "text":
                        voice_mode = False
                        print("  [Switched to text mode]\n")
                        continue
                    user_input = fallback
                else:
                    print(f"  You (voice): {user_input}")
            else:
                user_input = input("  You: ").strip()

            if not user_input:
                continue

            # Exit
            if user_input.lower() in (
                "quit", "exit", "bye", "stop"
            ):
                farewell = SanchiPersonality.get_farewell()
                print(f"\n  Sanchi: {farewell}\n")
                if voice_info["tts"]:
                    voice.speak(farewell)
                    time.sleep(3)
                break

            # Mode switching
            if user_input.lower() == "voice":
                if voice_info["stt"]:
                    voice_mode = True
                    print(
                        "  [Voice mode ON. "
                        "Say 'text' to switch back.]\n"
                    )
                else:
                    print(
                        "  [Voice not available. "
                        "Install SpeechRecognition & PyAudio.]\n"
                    )
                continue

            if user_input.lower() == "text":
                voice_mode = False
                print("  [Text mode ON.]\n")
                continue

            # Help
            if user_input.lower() in ("help", "/help"):
                print("\n  ╔════════════════════════════════╗")
                print("  ║     SANCHI AI - COMMANDS        ║")
                print("  ╠════════════════════════════════╣")
                print("  ║  voice  - Voice input mode      ║")
                print("  ║  text   - Text input mode       ║")
                print("  ║  help   - Show this help        ║")
                print("  ║  stats  - System info           ║")
                print("  ║  clear  - Reset conversation    ║")
                print("  ║  quit   - Exit Sanchi           ║")
                print("  ╚════════════════════════════════╝\n")
                continue

            # Stats
            if user_input.lower() in ("stats", "/stats"):
                print(f"\n  Backend: {stats['backend']}")
                print(f"  Model: {stats['model']}")
                print(f"  Messages: {brain.memory.messages.__len__()}")
                print(f"  Voice: {voice_info['tts_engine']}\n")
                continue

            # Clear
            if user_input.lower() in ("clear", "/clear"):
                response = brain.reset_conversation()
                print(f"\n  Sanchi: {response}\n")
                continue

            # Process message
            brain.set_verbal_mode(voice_mode)
            print("\n  Sanchi is thinking...")
            response = brain.think(user_input)
            print(f"\n  Sanchi: {response}\n")

            # Speak in voice mode
            if voice_mode and voice_info["tts"]:
                voice.speak(response)

        except KeyboardInterrupt:
            farewell = SanchiPersonality.get_farewell()
            print(f"\n\n  Sanchi: {farewell}\n")
            break
        except Exception as e:
            print(f"\n  [Error: {e}]\n")


# ================================================
# ENTRY POINT
# ================================================
if __name__ == "__main__":

    # Determine run mode
    mode = "gui"

    # Check command line arguments
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--mode" and i + 1 < len(sys.argv):
                mode = sys.argv[i + 1]
            elif arg in ("console", "text", "terminal"):
                mode = "console"

    # Run!
    if mode == "console" or not HAS_CTK:
        run_console_mode()
    else:
        try:
            app = SanchiGUI()
            app.mainloop()
        except Exception as e:
            print(f"\n[Error] GUI failed: {e}")
            print("[Info] Switching to console mode...\n")
            run_console_mode()
            
