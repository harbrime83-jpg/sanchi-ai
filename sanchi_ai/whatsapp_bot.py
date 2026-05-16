"""
Sanchi AI - WhatsApp Bot
Uses Twilio Sandbox (Free)
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from sanchi_core.brain import SanchiBrain

app = Flask(__name__)

# One brain instance for all conversations
# For multiple users, use a dict keyed by phone number
brain = SanchiBrain(backend="auto")

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    print(f"[WhatsApp] From: {sender} | Message: {incoming_msg}")

    # Get Sanchi's response
    response_text = brain.think(incoming_msg)

    # Send reply via Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    print("\n✅ Sanchi WhatsApp Bot is starting...")
    print("   Keep this running and start ngrok in another terminal")
    print("   Then paste the ngrok URL into Twilio Sandbox settings\n")
    app.run(port=5000, debug=True)