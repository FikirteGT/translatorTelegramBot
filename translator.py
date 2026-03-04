import os
import requests
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is not set")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

RESULTS_FILE = "results.txt"

# ------------------------
# Utility: log conversation
# ------------------------


def log_conversation(chat_id, english_text, amharic_text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"[{timestamp}]\n"
            f"Chat ID: {chat_id}\n"
            f"English: {english_text}\n"
            f"Amharic: {amharic_text}\n"
            f"{'-' * 40}\n"
        )

# ------------------------
# Health check
# ------------------------


@app.route("/", methods=["GET"])
def home():
    return "English → Amharic Translator Bot is running.", 200

# ------------------------
# Telegram webhook endpoint
# ------------------------


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # ------------------------
    # /start command
    # ------------------------
    if text == "/start":
        reply = (
            "Selam 👋\n"
            "Send me any English text and I will translate it to Amharic.\n\n"
            "Examples:\n"
            " - Hello, how are you?\n"
            " - I live in Addis Ababa."
        )
        send_message(chat_id, reply)
        return jsonify({"status": "ok"}), 200

    # ------------------------
    # /help command
    # ------------------------
    if text == "/help":
        reply = (
            "I am an English → Amharic translator bot.\n"
            "Just send English text, and I will reply in Amharic.\n\n"
            "Commands:\n"
            " /start  - introduction\n"
            " /help   - this help message"
        )
        send_message(chat_id, reply)
        return jsonify({"status": "ok"}), 200

    # ------------------------
    # Translation
    # ------------------------
    try:
        amharic_text = GoogleTranslator(
            source="auto",
            target="am"
        ).translate(text)

        reply = (
            "✅ Translation:\n\n"
            f"English:\n{text}\n\n"
            f"Amharic:\n{amharic_text}"
        )

        send_message(chat_id, reply)
        log_conversation(chat_id, text, amharic_text)

    except Exception as e:
        print("Translation error:", e)
        send_message(
            chat_id,
            "Sorry, I could not translate this right now. Please try again."
        )

    return jsonify({"status": "ok"}), 200


# ------------------------
# Send message helper
# ------------------------
def send_message(chat_id, text):
    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except Exception as e:
        print("Failed to send message:", e)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
