import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram settings
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Application environment
APP_ENV = os.getenv("APP_ENV", "dev")