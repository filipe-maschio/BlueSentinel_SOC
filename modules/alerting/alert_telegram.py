import time
import requests
import logging

from shared.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from shared.config import (
    TELEGRAM_MAX_MESSAGE_LENGTH,
    TELEGRAM_MAX_RETRIES,
    TELEGRAM_RETRY_DELAY,
    TELEGRAM_REQUEST_TIMEOUT,
)

log = logging.getLogger(__name__)


def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log.error("[Alert] Telegram credentials not set")
        raise ValueError("Missing Telegram credentials")

    if len(message) > TELEGRAM_MAX_MESSAGE_LENGTH:
        message = message[:TELEGRAM_MAX_MESSAGE_LENGTH] + "\n...[truncated]"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    for attempt in range(1, TELEGRAM_MAX_RETRIES + 1):
        try:
            log.info(f"[Alert] Sending alert (attempt {attempt}/{TELEGRAM_MAX_RETRIES})")

            response = requests.post(
                url,
                json=payload,
                timeout=TELEGRAM_REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                log.warning(f"[Alert] HTTP error {response.status_code}: {response.text}")
                raise RuntimeError("Telegram HTTP error")

            data = response.json()

            if not data.get("ok"):
                log.error(f"[Alert] Telegram API error: {data}")
                raise RuntimeError("Telegram API returned error")

            log.info("[Alert] Alert sent successfully to Telegram")
            return

        except requests.exceptions.RequestException as e:
            log.warning(f"[Alert] Network error on attempt {attempt}: {e}")

        except (RuntimeError, ValueError) as e:
            log.warning(f"[Alert] Attempt {attempt} failed: {e}")

        if attempt < TELEGRAM_MAX_RETRIES:
            delay = TELEGRAM_RETRY_DELAY * (2 ** (attempt - 1))
            log.info(f"[Alert] Retrying in {delay}s...")
            time.sleep(delay)

    log.error("[Alert] Failed to send alert after retries")
    raise RuntimeError("Telegram alert failed after retries")