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
├── streak_bot.py        # Main bot script
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
