# 🔥 TikTok Streak Bot

An automated bot that sends streak reminder messages to specified TikTok contacts using DrissionPage for browser automation.

## Features

- 🍪 **Cookie-based login** - Uses exported cookies (no login each time)
- 📋 **Contact list** - Specify exactly which users to message in `contacts.json`
- 📨 **Auto messaging** - Sends customizable streak reminders
- ⏰ **Daily scheduling** - Runs automatically at 7 AM
- 🛡️ **Anti-detection** - Uses DrissionPage to avoid automation checks

## Installation

### 1. Install Python Dependencies

```bash
cd "c:\Users\dewan\Desktop\Dew Project\TikTok Streak"
pip install -r requirements.txt
```

### 2. Setup Cookies

Export your TikTok cookies using a browser extension (like "Cookie-Editor" or "EditThisCookie") and save them to `cookies.json`.

The format should be an array of cookie objects:
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

### 3. Add Target Contacts

Edit `contacts.json` to add the TikTok usernames you want to message:

```json
{
    "contacts": [
        "friend1_username",
        "friend2_username",
        "friend3_username"
    ]
}
```

## Usage

### Run with Daily Schedule (Recommended)

```bash
python streak_bot.py
```

Runs at 7:00 AM daily. Keep terminal open.

### Run Immediately

```bash
python streak_bot.py --now
```

Sends messages right away, then exits.

### Test Mode

```bash
python streak_bot.py --test
```

Finds contacts but **doesn't send messages**. Useful for testing.

### Custom Message

```bash
python streak_bot.py --now --message "Streak hari ini! 🔥"
```

Send custom message without editing `config.py`. Works with `--now` and `--test`:

```bash
# Test with custom message
python streak_bot.py --test -m "Jangan lupa streak kita!"

# Send immediately with custom message
python streak_bot.py --now --message "Streak reminder from Dew"
```

### Show Help

```bash
python streak_bot.py --help
```

Shows all available commands and options.

## 🤖 Telegram Bot Controller

Control bot via Telegram! Manage kontak, ganti message, dan kirim streak langsung dari Telegram.

### Setup Telegram Bot

1. Make sure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are configured in `config.py`
2. Run the main bot (includes Telegram controller + scheduler):

```bash
python main.py
```

Keep this running - bot will listen for Telegram commands AND run scheduled streaks.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message & help | `/start` |
| `/text [message]` | Change streak message | `/text Streak hari ini! 🔥` |
| `/send` | Send messages immediately | `/send` |
| `/test` | Test mode (find contacts, no send) | `/test` |
| `/status` | Show current configuration | `/status` |
| `/help` | Show help message | `/help` |

### Usage Examples

**Ganti message:**
```
/text Jangan lupa streak kita ya!
```

**Kirim sekarang:**
```
/send
```

**Test dulu (cek kontak tanpa kirim):**
```
/test
```

**Cek status & message saat ini:**
```
/status
```

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `STREAK_MESSAGE` | `"Streak reminder -Dew Bot"` | Message to send |
| `SCHEDULE_TIME` | `"07:00"` | Daily run time (24h format) |
| `HEADLESS_MODE` | `False` | Run without visible browser |
| `MESSAGE_SEND_DELAY` | `2` | Seconds between messages |

## File Structure

```
TikTok Streak/
├── main.py              # Main entry: Telegram bot + scheduler ⭐
├── streak_bot.py        # Core bot logic
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── cookies.json         # Your TikTok cookies (export from browser)
├── contacts.json        # List of usernames to message
├── logs/                # Log files
│   └── streak_bot_YYYYMMDD.log
└── README.md            # This file
```

## Troubleshooting

### "Cookies file not found"
Export your TikTok cookies to `cookies.json` using a browser extension.

### "Not logged in - redirected to login page"
Your cookies have expired. Export fresh cookies from your browser.

### "Could not find these contacts"
Make sure the usernames in `contacts.json` match exactly and that you have an existing conversation with them.

## Logs

Logs are saved to the `logs/` directory with daily rotation:
- `streak_bot_20260109.log`

## ⚠️ Disclaimer

This bot is for educational purposes. Automated actions may violate TikTok's Terms of Service. Use responsibly and at your own risk.
