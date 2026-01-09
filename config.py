# TikTok Streak Bot Configuration

import os

# =============================================================================
# TikTok URLs
# =============================================================================
TIKTOK_BASE_URL = "https://www.tiktok.com"
TIKTOK_MESSAGES_URL = "https://www.tiktok.com/messages"
TIKTOK_LOGIN_URL = "https://www.tiktok.com/login"

# =============================================================================
# Message Settings
# =============================================================================
STREAK_MESSAGE = "🔥 Streak Reminder 🔥 - Dew Bot"

# =============================================================================
# Schedule Settings
# =============================================================================
# Time to send streak messages (24-hour format)
SCHEDULE_TIME = "07:00"

# =============================================================================
# Telegram Notification Settings
# =============================================================================
# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "8568089554:AAERJBWnVY5W4iGxbkOoRQRJ50YBcGPFsLk"

# Get your chat ID from @userinfobot or @get_id_bot on Telegram  
TELEGRAM_CHAT_ID = "5673885457"

# Enable/disable Telegram notifications
TELEGRAM_ENABLED = True

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
# Headless mode (set to True to run without visible browser)
HEADLESS_MODE = False

# Wait times (in seconds)
PAGE_LOAD_WAIT = 5
ELEMENT_WAIT = 3
MESSAGE_SEND_DELAY = 2  # Delay between sending messages to avoid rate limiting

# =============================================================================
# Logging Settings
# =============================================================================
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
