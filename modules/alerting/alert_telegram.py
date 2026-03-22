import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_LEN = 4000
MAX_RETRIES = 5
RETRY_DELAY = 2  # segundos


def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials not set")
        return

    if len(message) > MAX_LEN:
        message = message[:MAX_LEN] + "\n...[truncated]"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"📡 Sending alert (attempt {attempt}/{MAX_RETRIES})...")

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print("✅ Alert sent successfully to Telegram")
                return
            else:
                print(f"⚠️ Attempt {attempt} failed: {response.text}")

        except Exception as e:
            print(f"⚠️ Attempt {attempt}/{MAX_RETRIES} failed")

            if attempt == MAX_RETRIES:
                print(f"❌ Final error: {str(e)[:150]}")

        # espera antes do próximo retry
        if attempt < MAX_RETRIES:
            print(f"⏳ Retrying in {RETRY_DELAY}s...\n")
            time.sleep(RETRY_DELAY)

    print("🚨 Failed to send alert after multiple attempts")