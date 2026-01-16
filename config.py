# TikTok Streak Bot Configuration
# Created by: dewhush
#
# All sensitive values are loaded from environment variables.
# Copy .env.example to .env and fill in your values.

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# TikTok URLs
# =============================================================================
TIKTOK_BASE_URL = "https://www.tiktok.com"
TIKTOK_MESSAGES_URL = "https://www.tiktok.com/messages"
TIKTOK_LOGIN_URL = "https://www.tiktok.com/login"

# =============================================================================
# API Settings
# =============================================================================
APP_NAME = os.getenv("APP_NAME", "TikTok Streak API")
APP_ENV = os.getenv("APP_ENV", "development")
API_KEY = os.getenv("API_KEY", "")

# =============================================================================
# Message Settings
# =============================================================================
STREAK_MESSAGE = os.getenv("STREAK_MESSAGE", "🔥 Streak Reminder 🔥 - Dew Bot")

# =============================================================================
# Schedule Settings
# =============================================================================
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "00:00")

# =============================================================================
# Telegram Notification Settings
# =============================================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"
TELEGRAM_LOG_ENABLED = os.getenv("TELEGRAM_LOG_ENABLED", "true").lower() == "true"

# Minimum log level to send to Telegram (INFO, WARNING, ERROR)
_log_level = os.getenv("TELEGRAM_LOG_LEVEL", "WARNING").upper()
TELEGRAM_LOG_LEVEL = getattr(logging, _log_level, logging.WARNING)

# =============================================================================
# File Paths
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.json")
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts.json")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

# =============================================================================
# Browser Settings
# =============================================================================
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "false").lower() == "true"

# Wait times (in seconds)
PAGE_LOAD_WAIT = int(os.getenv("PAGE_LOAD_WAIT", "5"))
ELEMENT_WAIT = int(os.getenv("ELEMENT_WAIT", "3"))
MESSAGE_SEND_DELAY = int(os.getenv("MESSAGE_SEND_DELAY", "2"))

# =============================================================================
# Server Settings
# =============================================================================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# =============================================================================
# Logging Settings
# =============================================================================
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
