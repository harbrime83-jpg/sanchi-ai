"""
Sanchi AI - Chat Screen Components
Built with CustomTkinter for modern dark UI.
"""

import customtkinter as ctk
from datetime import datetime


class MessageBubble(ctk.CTkFrame):
    """A single chat message bubble."""

    def __init__(self, master, text, is_user=True, **kwargs):
        super().__init__(master, **kwargs)

        # Colors
        if is_user:
            bubble_color = "#1a5276"
            text_color = "#ffffff"
            sender = "You"
            sender_color = "#5dade2"
            anchor = "e"
            padx_left = 80
            padx_right = 10
        else:
            bubble_color = "#2c3e50"
            text_color = "#ecf0f1"
            sender = "✨ Sanchi"
            sender_color = "#e91e8c"
            anchor = "w"
            padx_left = 10
            padx_right = 80

        # Make frame transparent
        self.configure(fg_color="transparent")

        # Container for alignment
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(
            fill="x",
            padx=(padx_left, padx_right),
            pady=2,
            anchor=anchor,
        )

        # Sender name + timestamp
        time_str = datetime.now().strftime("%I:%M %p")
        header = ctk.CTkLabel(
            container,
            text=f"{sender}  •  {time_str}",
            font=("Segoe UI", 11),
            text_color=sender_color,
            anchor="w",
        )
        header.pack(fill="x", padx=5, pady=(2, 0))

        # Message bubble
        bubble = ctk.CTkFrame(
            container,
            fg_color=bubble_color,
            corner_radius=15,
        )
        bubble.pack(fill="x", padx=0, pady=(2, 4))

        # Message text
        msg_label = ctk.CTkLabel(
            bubble,
            text=text,
            font=("Segoe UI", 14),
            text_color=text_color,
            wraplength=350,
            justify="left",
            anchor="w",
        )
        msg_label.pack(
            padx=15,
            pady=10,
            fill="x",
            anchor="w",
        )


class TypingIndicator(ctk.CTkFrame):
    """Shows 'Sanchi is thinking...' animation."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        container.pack(fill="x", padx=10, pady=2, anchor="w")

        self.label = ctk.CTkLabel(
            container,
            text="✨ Sanchi is thinking...",
            font=("Segoe UI", 12, "italic"),
            text_color="#e91e8c",
            anchor="w",
        )
        self.label.pack(padx=10, pady=5)

        self.dots = 0
        self._animate()

    def _animate(self):
        """Animate the dots."""
        self.dots = (self.dots + 1) % 4
        dot_text = "." * self.dots
        try:
            self.label.configure(
                text=f"✨ Sanchi is thinking{dot_text}"
            )
            self.after(500, self._animate)
        except Exception:
            pass  # Widget destroyed


class ChatScrollFrame(ctk.CTkScrollableFrame):
    """Scrollable frame for chat messages."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#1a1a2e")

    def add_message(self, text, is_user=True):
        """Add a message bubble to the chat."""
        bubble = MessageBubble(
            self,
            text=text,
            is_user=is_user,
        )
        bubble.pack(fill="x", pady=2)

        # Auto-scroll to bottom
        self.after(100, self._scroll_to_bottom)

        return bubble

    def add_typing_indicator(self):
        """Show typing indicator."""
        indicator = TypingIndicator(self)
        indicator.pack(fill="x", pady=2)
        self.after(100, self._scroll_to_bottom)
        return indicator

    def _scroll_to_bottom(self):
        """Scroll to the bottom of chat."""
        try:
            self._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def clear_all(self):
        """Clear all messages."""
        for widget in self.winfo_children():
            widget.destroy()