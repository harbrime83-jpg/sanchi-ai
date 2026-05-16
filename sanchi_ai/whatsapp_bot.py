"""
Sanchi AI - WhatsApp Bot (Server Version)
No GUI, No Voice - Web only
"""

import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# AI
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

app = Flask(__name__)

# Store conversations per user
conversations = {}

SYSTEM_PROMPT = """You are Sanchi, a highly intelligent, articulate and charismatic female AI assistant. You are warm but intellectually sharp. You give real, actionable advice. You are deeply knowledgeable about business, human psychology, personality development, dark psychology, persuasion, emotional intelligence, and life strategy. You speak like a knowledgeable friend who genuinely cares. Be conversational, not robotic."""

def get_ai_response(user_phone, user_message):
    """Get response from Groq AI."""
    
    # Initialize conversation for new users
    if user_phone not in conversations:
        conversations[user_phone] = [
            {"role": "user", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Understood! I am Sanchi, ready to help."}
        ]
    
    # Add user message
    conversations[user_phone].append({
        "role": "user",
        "content": user_message
    })
    
    # Keep conversation short to save memory
    if len(conversations[user_phone]) > 20:
        conversations[user_phone] = conversations[user_phone][:2] + conversations[user_phone][-18:]
    
    try:
        if HAS_GROQ and os.getenv("GROQ_API_KEY"):
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=conversations[user_phone],
                temperature=0.8,
                max_tokens=500,
            )
            reply = response.choices[0].message.content.strip()
        else:
            reply = "Hey! I'm Sanchi. My AI brain isn't connected yet - check the GROQ_API_KEY setting."
            
    except Exception as e:
        print(f"[Error] {e}")
        reply = "I had a small hiccup! Try again in a moment."
    
    # Save reply to conversation
    conversations[user_phone].append({
        "role": "assistant",
        "content": reply
    })
    
    return reply


@app.route("/")
def home():
    return "Sanchi AI is running! 🤖"


@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    print(f"[WhatsApp] From: {sender} | Message: {incoming_msg}")

    reply = get_ai_response(sender, incoming_msg)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n✅ Sanchi WhatsApp Bot running on port {port}")
    app.run(host="0.0.0.0", port=port)
