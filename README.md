# 🔥 TikTok Streak API

Automated TikTok streak reminder bot with REST API and Telegram bot controller.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🍪 **Cookie-based login** - No login required each time
- 📨 **Auto messaging** - Sends customizable streak reminders
- ⏰ **Daily scheduling** - Runs automatically at configured time
- 🌐 **REST API** - Control bot via HTTP endpoints
- 🤖 **Telegram Bot** - Manage contacts and trigger from Telegram
- 🛡️ **Anti-detection** - Uses DrissionPage to avoid automation checks

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/dewhush/TikTok-Streak-API.git
cd TikTok-Streak-API
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Export TikTok Cookies

1. Install browser extension: **Cookie-Editor** or **EditThisCookie**
2. Login to TikTok in your browser
3. Export cookies as JSON
4. Save to `cookies.json` in project folder

Example format:
```json
[
    {
        "domain": ".tiktok.com",
        "name": "sessionid",
        "value": "your_session_id",
        ...
    }
]
```

### 4. Add Target Contacts

Create `contacts.json`:
```json
{
    "contacts": [
        "friend1_nickname",
        "friend2_nickname"
    ]
}
```

> **Note:** Use the **display name/nickname** shown in TikTok messages, not username.

### 5. Configure Settings

Edit `config.py`:
```python
TELEGRAM_BOT_TOKEN = "your-bot-token"  # From @BotFather
TELEGRAM_CHAT_ID = "your-chat-id"      # From @userinfobot
SCHEDULE_TIME = "07:00"                 # Daily run time (24h format)
STREAK_MESSAGE = "🔥 Streak!"           # Message to send
```

---

## 📖 Usage

### Option 1: REST API

```bash
# Start API server
python -m uvicorn api:app --host 0.0.0.0 --port 8000

# Or use the batch file (Windows)
run_api.bat
```

**Swagger Docs:** http://localhost:8000/docs

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Get bot status |
| `GET` | `/api/contacts` | List contacts |
| `POST` | `/api/contacts` | Add contact |
| `DELETE` | `/api/contacts/{nickname}` | Remove contact |
| `POST` | `/api/run` | Run streak bot |

#### Authentication

All requests need `X-API-Key` header:
```bash
curl -H "X-API-Key: your-secret-api-key-here" http://localhost:8000/api/status
```

Set API key via environment variable `TIKTOK_API_KEY` or edit `api.py`.

---

### Option 2: Telegram Bot

```bash
python main.py

# Or use the batch file (Windows)
run_tiktok_streak.bat
```

#### Telegram Commands

| Command | Description |
|---------|-------------|
| `/add {nickname}` | Add contact |
| `/remove {nickname}` | Remove contact |
| `/list` | Show all contacts |
| `/text {message}` | Change streak message |
| `/run` | Run streak bot now |
| `/status` | Show bot status |

---

### Option 3: Direct Script

```bash
# Run immediately
python streak_bot.py --now

# Test mode (find contacts, don't send)
python streak_bot.py --test

# Custom message
python streak_bot.py --now --message "Streak hari ini! 🔥"

# Schedule mode (runs at configured time)
python streak_bot.py
```

---

## 📁 File Structure

```
TikTok-Streak-API/
├── api.py               # REST API (FastAPI)
├── main.py              # Telegram bot + scheduler
├── streak_bot.py        # Core bot logic
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── cookies.json         # Your TikTok cookies (create this)
├── contacts.json        # Target contacts (create this)
├── run_api.bat          # Start API server (Windows)
├── run_tiktok_streak.bat # Start Telegram bot (Windows)
└── logs/                # Log files
```

---

## ⚙️ Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `STREAK_MESSAGE` | `"🔥 Streak Reminder 🔥"` | Message to send |
| `SCHEDULE_TIME` | `"00:00"` | Daily run time (24h) |
| `HEADLESS_MODE` | `False` | Run without visible browser |
| `TELEGRAM_ENABLED` | `True` | Enable Telegram notifications |

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| "Cookies file not found" | Export TikTok cookies to `cookies.json` |
| "Not logged in" | Cookies expired, export fresh cookies |
| "Could not find contacts" | Check nickname matches exactly (case-sensitive) |
| "Bot timed out" | Auto-retries 3x, check for TikTok popups |

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Automated actions may violate TikTok's Terms of Service. Use responsibly and at your own risk.

---

## 📄 License

MIT License - feel free to use and modify!

---

Made with ❤️ by [dewhush](https://github.com/dewhush)
