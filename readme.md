# 🌍 Telegram Translator Bot

A simple Telegram bot that automatically translates any message into Amharic 🇪🇹.

Built with:

- Python
- Flask
- deep-translator
- Deployed on Render

---

## 🚀 How It Works

1. User sends a message
2. Telegram sends update to /webhook
3. The bot translates the message
4. Sends back the Amharic version

---

## ⚙️ Environment Variables

Set these in Render:

BOT_TOKEN=your_telegram_bot_token
WEBHOOK_URL=https://translatortelegrambot-ikpg.onrender.com

---

## 🛠 Run with

Build:

pip install -r requirements.txt


Start:

gunicorn translator:app


---

Simple, lightweight, and production-ready. 🚀