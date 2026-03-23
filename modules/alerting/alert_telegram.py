import os
import time
import requests
from dotenv import load_dotenv
import logging

log = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_LEN = 4000
MAX_RETRIES = 5
RETRY_DELAY = 2  # segundos


def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log.error("Telegram credentials not set")
        raise ValueError("Missing Telegram credentials")

    if len(message) > MAX_LEN:
        message = message[:MAX_LEN] + "\n...[truncated]"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info(f"Sending alert (attempt {attempt}/{MAX_RETRIES})")

            response = requests.post(url, json=payload, timeout=10)  # TODO: move to config

            if response.status_code != 200:
                log.warning(f"HTTP error {response.status_code}: {response.text}")
                raise RuntimeError("Telegram HTTP error")

            try:
                data = response.json()
            except ValueError:
                log.error(f"Invalid JSON response: {response.text[:200]}")
                raise RuntimeError("Invalid Telegram response")
            if not data.get("ok"):
                log.error(f"Telegram API error: {data}")
                raise RuntimeError("Telegram API returned error")

            log.info("Alert sent successfully to Telegram")
            return

        except requests.exceptions.RequestException as e:
            log.warning(f"Network error on attempt {attempt}: {e}")

        except (RuntimeError, ValueError) as e:
            log.warning(f"Attempt {attempt} failed: {e}")

        if attempt < MAX_RETRIES:
            delay = RETRY_DELAY * (2 ** (attempt - 1))
            log.info(f"Retrying in {delay}s...")
            time.sleep(delay)

    log.error("Failed to send alert after retries")
    raise RuntimeError("Telegram alert failed after retries")