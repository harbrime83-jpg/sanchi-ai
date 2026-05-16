"""
Sanchi's Brain - Core AI Engine
Handles conversation, context management, and AI model integration.
"""

import os
import json
import time
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try importing AI libraries
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from .personality import SanchiPersonality


class ConversationMemory:
    """Manages conversation history and context."""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.messages = []
        self.session_start = datetime.now()
        self.user_profile = {}
        self.topic_history = []

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.messages.append(
            {"role": role, "content": content, "timestamp": time.time()}
        )
        if len(self.messages) > self.max_history:
            self.messages = (
                self.messages[:1] + self.messages[-(self.max_history - 1):]
            )

    def get_messages_for_api(self) -> list:
        """Get messages formatted for API calls."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages
        ]

    def clear(self):
        """Clear conversation history."""
        self.messages = []
        self.topic_history = []

    def get_context_summary(self) -> str:
        """Get a brief summary of conversation context."""
        if not self.messages:
            return "New conversation"
        return f"Conversation with {len(self.messages)} messages"

    def save_to_file(self, filepath: str = "conversation_history.json"):
        """Save conversation to file."""
        data = {
            "session_start": self.session_start.isoformat(),
            "messages": self.messages,
            "user_profile": self.user_profile,
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: str = "conversation_history.json"):
        """Load conversation from file."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                self.messages = data.get("messages", [])
                self.user_profile = data.get("user_profile", {})
        except FileNotFoundError:
            pass


class SanchiBrain:
    """
    Main AI brain for Sanchi.
    Supports: OpenAI, Groq (free), and local fallback.
    """

    def __init__(self, backend: str = "auto"):
        self.memory = ConversationMemory()
        self.personality = SanchiPersonality()
        self.backend = self._select_backend(backend)
        self.client = None
        self.model = None
        self.is_verbal_mode = False

        self._initialize_client()
        self._initialize_conversation()

        print(f"[Sanchi Brain] Initialized with backend: {self.backend}")

    def _select_backend(self, preferred: str) -> str:
        """Select the best available backend."""
        if preferred != "auto":
            return preferred

        if (
            os.getenv("OPENAI_API_KEY")
            and os.getenv("OPENAI_API_KEY") != "your_openai_key_here"
            and HAS_OPENAI
        ):
            return "openai"
        elif (
            os.getenv("GROQ_API_KEY")
            and os.getenv("GROQ_API_KEY") != "paste_your_key_here"
            and HAS_GROQ
        ):
            return "groq"
        else:
            return "local"

    def _initialize_client(self):
        """Initialize the AI client based on backend."""
        if self.backend == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            print(f"[Sanchi Brain] Using OpenAI: {self.model}")

        elif self.backend == "groq":
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            print(f"[Sanchi Brain] Using Groq: {self.model}")

        elif self.backend == "local":
            print("[Sanchi Brain] Using local fallback mode")
            self.client = None
            self.model = "local"

    def _initialize_conversation(self):
        """Set up the initial conversation with system prompt."""
        system_prompt = self.personality.get_system_prompt()
        self.memory.add_message("system", system_prompt)

    def set_verbal_mode(self, enabled: bool):
        """Toggle verbal/text mode for response length."""
        self.is_verbal_mode = enabled

    def think(self, user_input: str) -> str:
        """
        Process user input and generate a response.
        """
        if not user_input.strip():
            return "I didn't catch that. Could you say it again?"

        mode_hint = ""
        if self.is_verbal_mode:
            mode_hint = (
                "\n[SYSTEM: User is speaking verbally. "
                "Keep response concise - 2-4 sentences for simple questions.]"
            )

        self.memory.add_message("user", user_input + mode_hint)

        try:
            if self.backend in ("openai", "groq"):
                response = self._api_response()
            else:
                response = self._local_response(user_input)
        except Exception as e:
            print(f"[Sanchi Brain] Error: {e}")
            response = self._fallback_response(user_input)

        self.memory.add_message("assistant", response)
        return response

    def _api_response(self) -> str:
        """Generate response using OpenAI or Groq API."""
        messages = self.memory.get_messages_for_api()

        try:
            if self.backend == "groq":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=1024 if not self.is_verbal_mode else 256,
                    top_p=0.9,
                )
            else:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=1024 if not self.is_verbal_mode else 256,
                    top_p=0.9,
                    frequency_penalty=0.3,
                    presence_penalty=0.3,
                )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Sanchi Brain] API Error: {e}")
            raise

    def _local_response(self, user_input: str) -> str:
        """Local fallback responses when no API is available."""
        user_lower = user_input.lower()

        responses = {
            "hello": "Hey there! I'm Sanchi. What's on your mind today?",
            "hi": "Hi! Good to hear from you. What can I help you with?",
            "hey": "Hey! I'm all ears. What do you want to talk about?",
            "how are you": (
                "I'm doing great, thanks for asking! "
                "I'm always ready for a good conversation. What's up?"
            ),
            "business": (
                "Business is all about solving problems profitably. "
                "The best businesses find a real pain point and fix it better "
                "than anyone else. What specific aspect are you thinking about - "
                "starting up, scaling, marketing, or strategy?"
            ),
            "startup": (
                "Starting a business? Here's what matters most: "
                "1) Validate your idea before building. Talk to 50 potential customers. "
                "2) Start lean - MVP first, perfection never. "
                "3) Focus on revenue from day one, not just the product. "
                "What kind of startup are you thinking about?"
            ),
            "marketing": (
                "Marketing is just applied psychology. You need to understand "
                "your customer's desires, fears, and decision-making patterns. "
                "The best marketing doesn't feel like marketing - it feels like "
                "someone finally understanding your problem. What are you marketing?"
            ),
            "dark psychology": (
                "Dark psychology studies how people use psychological tactics "
                "for manipulation. Key concepts include: "
                "gaslighting, love bombing, social proof exploitation, "
                "and emotional leverage. I teach this for AWARENESS - "
                "knowing these tactics helps you spot and defend against them. "
                "What specifically do you want to understand?"
            ),
            "manipulation": (
                "Manipulation works by exploiting emotional vulnerabilities. "
                "Common tactics: 1) Reciprocity traps - doing favors to create obligation. "
                "2) Scarcity pressure - 'Act now or lose it.' "
                "3) Social proof - 'Everyone else is doing it.' "
                "4) Authority play - using status to bypass critical thinking. "
                "Awareness is your shield. What situation are you dealing with?"
            ),
            "personality": (
                "Personality development isn't about becoming someone else - "
                "it's about becoming the best version of who you already are. "
                "Focus on: emotional intelligence, communication skills, "
                "confidence building, and self-awareness. "
                "Which area resonates with you most?"
            ),
            "confidence": (
                "Real confidence comes from competence plus self-acceptance. "
                "It's not about feeling no fear - it's about acting despite it. "
                "Three practical steps: 1) Track your wins daily. "
                "2) Put yourself in uncomfortable situations regularly. "
                "3) Stop comparing your chapter 1 to someone's chapter 20."
            ),
            "love": (
                "Love is beautiful but complex. The healthiest relationships "
                "are built on mutual respect, clear communication, and individual "
                "growth. Remember - you can't pour from an empty cup. "
                "What's on your heart?"
            ),
            "money": (
                "Money is a tool, not a goal. The formula is simple: "
                "1) Increase your income through skills. "
                "2) Decrease unnecessary spending. "
                "3) Invest the difference consistently. "
                "What specific money question do you have?"
            ),
        }

        for keyword, response in responses.items():
            if keyword in user_lower:
                return response

        return (
            "That's an interesting topic! I'm currently in local mode "
            "without my full AI capabilities. To unlock my full potential, "
            "set up a FREE Groq API key in the .env file. "
            "But I can still chat about business, psychology, personality "
            "development, and more. Try asking me about those!"
        )

    def _fallback_response(self, user_input: str) -> str:
        """Emergency fallback if everything fails."""
        return (
            "I had a brief hiccup processing that. "
            "Could you rephrase or try again? I'm still here for you."
        )

    def reset_conversation(self):
        """Reset the conversation history."""
        self.memory.clear()
        self._initialize_conversation()
        return "Conversation reset. Fresh start! What's on your mind?"

    def get_stats(self) -> dict:
        """Get conversation statistics."""
        return {
            "backend": self.backend,
            "model": self.model,
            "messages": len(self.memory.messages),
            "session_start": self.memory.session_start.isoformat(),
        }