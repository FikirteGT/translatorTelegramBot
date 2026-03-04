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


def log_conversation(chat_id, user_text, translated_text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"[{timestamp}]\n"
            f"Chat ID: {chat_id}\n"
            f"User: {user_text}\n"
            f"Amharic: {translated_text}\n"
            f"{'-'*40}\n"
        )

# ------------------------
# Set webhook immediately on startup
# ------------------------


def register_webhook():
    try:
        requests.post(
            f"{TELEGRAM_API}/setWebhook",
            json={"url": f"{WEBHOOK_URL}/webhook"},
            timeout=10
        )
        print("Webhook registered successfully.")
    except Exception as e:
        print("Webhook registration failed:", e)


# register_webhook()

# ------------------------
# Health check route
# ------------------------


@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

# ------------------------
# Telegram webhook endpoint
# ------------------------


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 400

    message = data.get("message")

    if message and "text" in message:
        chat_id = message["chat"]["id"]
        user_text = message["text"]

        if user_text.startswith("/"):
            reply = "Send me any message and I will translate it to Amharic."
        else:
            try:
                translated = GoogleTranslator(
                    source="auto",
                    target="am"
                ).translate(user_text)

                reply = f"Translated to Amharic:\n{translated}"

                # 🔥 Log conversation
                log_conversation(chat_id, user_text, translated)

            except Exception:
                reply = "Translation error occurred."

        try:
            requests.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": reply
                },
                timeout=10
            )
        except Exception as e:
            print("Failed to send message:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
