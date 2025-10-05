import requests
import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # или вставь токен напрямую
RENDER_URL = "https://wq-bot3.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
print(response.json())
