"""
Test script to check what's installed and working.
Run: python test_setup.py
"""

import sys

print("\n" + "=" * 50)
print("  SANCHI AI - System Check")
print("=" * 50)
print(f"\n  Python: {sys.version}")

# Check each package
packages = {
    "dotenv": "python-dotenv",
    "openai": "openai",
    "groq": "groq",
    "flask": "flask",
    "requests": "requests",
    "speech_recognition": "SpeechRecognition",
    "pyttsx3": "pyttsx3",
    "gtts": "gTTS",
    "customtkinter": "customtkinter",
    "PIL": "Pillow",
    "pyngrok": "pyngrok",
    "twilio": "twilio",
    "telegram": "python-telegram-bot",
    "discord": "discord.py",
}

print("\n  Package Status:")
print("  " + "-" * 40)

installed = 0
failed = 0

for module, package in packages.items():
    try:
        __import__(module)
        print(f"  ✅ {package:30s} Installed")
        installed += 1
    except ImportError:
        print(f"  ❌ {package:30s} NOT installed")
        failed += 1

print("  " + "-" * 40)
print(f"  Installed: {installed}/{installed + failed}")
print(f"  Missing:   {failed}")

# Check pyngrok specifically
print("\n  Ngrok Check:")
print("  " + "-" * 40)
try:
    from pyngrok import ngrok
    print("  ✅ pyngrok imported successfully")
    
    try:
        version = ngrok.get_version()
        print(f"  ✅ ngrok binary found: v{version}")
    except Exception as e:
        print(f"  ⚠️  ngrok binary issue: {e}")
        print("  → Try: download ngrok manually")
        print("     https://ngrok.com/download")
except ImportError:
    print("  ❌ pyngrok not installed")
    print("  → Run: pip install pyngrok")
    print("  → OR skip it! Use Polling mode")
except Exception as e:
    print(f"  ⚠️  pyngrok error: {e}")

# Check microphone
print("\n  Audio Check:")
print("  " + "-" * 40)
try:
    import speech_recognition as sr
    mics = sr.Microphone.list_microphone_names()
    print(f"  ✅ Microphones found: {len(mics)}")
    if mics:
        print(f"     Default: {mics[0][:40]}")
except Exception as e:
    print(f"  ⚠️  Mic check: {e}")

# Summary
print("\n" + "=" * 50)
print("  RECOMMENDATION:")
if failed == 0:
    print("  ✅ Everything installed! You're ready!")
else:
    print(f"  Install missing packages:")
    for module, package in packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"     pip install {package}")

print("\n  WHAT YOU CAN RUN:")
try:
    __import__("customtkinter")
    print("  ✅ Desktop App:  python main.py")
except ImportError:
    print("  ❌ Desktop App:  Install customtkinter")

print("  ✅ Console Mode: python main.py --mode console")

try:
    __import__("flask")
    print("  ✅ WhatsApp Bot: python whatsapp_bot.py")
except ImportError:
    print("  ❌ WhatsApp Bot: Install flask")

try:
    __import__("telegram")
    print("  ✅ Telegram Bot: python telegram_bot.py")
except ImportError:
    print("  ❌ Telegram Bot: Install python-telegram-bot")

try:
    __import__("discord")
    print("  ✅ Discord Bot:  python discord_bot.py")
except ImportError:
    print("  ❌ Discord Bot:  Install discord.py")

print("=" * 50 + "\n")