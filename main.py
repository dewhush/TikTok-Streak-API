"""
TikTok Streak Bot - Combined
=============================
Telegram bot controller + scheduled streak sending in one script.

Features:
- Telegram commands: /add, /remove, /list, /run
- Automatic streak sending at scheduled time (default: 7 AM)

Usage:
    python main.py
"""

import json
import os
import sys
import time
import logging
import threading
import asyncio
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import schedule

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    CONTACTS_FILE,
    LOGS_DIR,
    SCHEDULE_TIME,
    HEADLESS_MODE,
    STREAK_MESSAGE,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)

# Global variable for custom message
custom_message = None


# Set up logging
def setup_logging():
    """Configure logging to both file and console."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = os.path.join(LOGS_DIR, f"streak_bot_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# =============================================================================
# Contact Management Functions
# =============================================================================

def load_contacts():
    """Load contacts from JSON file."""
    if not os.path.exists(CONTACTS_FILE):
        return []
    
    try:
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('contacts', [])
    except:
        return []


def save_contacts(contacts):
    """Save contacts to JSON file."""
    try:
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"contacts": contacts}, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving contacts: {e}")
        return False


# =============================================================================
# Telegram Bot Handlers
# =============================================================================

def is_authorized(update: Update) -> bool:
    """Check if user is authorized (matches TELEGRAM_CHAT_ID)."""
    user_id = str(update.effective_user.id)
    return user_id == TELEGRAM_CHAT_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "<b>TikTok Streak Bot Controller</b>\n\n"
        "Manage your streak contacts with these commands:\n\n"
        "<b>Commands:</b>\n"
        "/add {nickname} - Add a contact\n"
        "/remove {nickname} - Remove a contact\n"
        "/list - Show all contacts\n"
        "/text {message} - Change streak message\n"
        "/status - Show current config\n"
        "/run - Run streak bot now\n"
        "/help - Show this message",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "<b>TikTok Streak Bot - Help</b>\n\n"
        "<b>Available Commands:</b>\n\n"
        "/add {nickname} - Add contact\n"
        "/remove {nickname} - Remove contact\n"
        "/list - Show all contacts\n"
        "/text {message} - Change streak message\n"
        "/status - Show current config\n"
        "/run - Run streak bot now\n"
        "/help - Show this message\n\n"
        f"<b>Scheduled:</b> Daily at {SCHEDULE_TIME}",
        parse_mode='HTML'
    )


async def add_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command."""
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a nickname.\n\n"
            "Usage: <code>/add {nickname}</code>\n"
            "Example: <code>/add Dew</code>",
            parse_mode='HTML'
        )
        return
    
    nickname = ' '.join(context.args)
    contacts = load_contacts()
    
    if nickname.lower() in [c.lower() for c in contacts]:
        await update.message.reply_text(
            f"<b>{nickname}</b> is already in the streak list!",
            parse_mode='HTML'
        )
        return
    
    contacts.append(nickname)
    
    if save_contacts(contacts):
        await update.message.reply_text(
            f"<b>{nickname}</b> added to streak list!\n\n"
            f"Total contacts: {len(contacts)}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("Failed to save contact. Please try again.")


async def remove_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remove command."""
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a nickname.\n\n"
            "Usage: <code>/remove {nickname}</code>\n"
            "Example: <code>/remove Dew</code>",
            parse_mode='HTML'
        )
        return
    
    nickname = ' '.join(context.args)
    contacts = load_contacts()
    
    original_count = len(contacts)
    contacts = [c for c in contacts if c.lower() != nickname.lower()]
    
    if len(contacts) == original_count:
        await update.message.reply_text(
            f"<b>{nickname}</b> not found in streak list.",
            parse_mode='HTML'
        )
        return
    
    if save_contacts(contacts):
        await update.message.reply_text(
            f"<b>{nickname}</b> removed from streak list!\n\n"
            f"Remaining contacts: {len(contacts)}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("Failed to save changes. Please try again.")


async def list_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command."""
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    contacts = load_contacts()
    
    if not contacts:
        await update.message.reply_text(
            "<b>Streak Contacts</b>\n\n"
            "No contacts added yet.\n"
            "Use /add {nickname} to add one!",
            parse_mode='HTML'
        )
        return
    
    contact_list = '\n'.join([f"  - {c}" for c in contacts])
    
    await update.message.reply_text(
        f"<b>Streak Contacts</b> ({len(contacts)})\n\n"
        f"{contact_list}",
        parse_mode='HTML'
    )


async def text_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /text command to change streak message."""
    global custom_message
    
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "<b>Change Streak Message</b>\n\n"
            "Please provide a message!\n\n"
            "<b>Usage:</b>\n"
            "<code>/text Streak hari ini! 🔥</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/text Jangan lupa streak kita ya!</code>",
            parse_mode='HTML'
        )
        return
    
    new_message = ' '.join(context.args)
    custom_message = new_message
    
    logger.info(f"Streak message changed via Telegram: {new_message}")
    
    await update.message.reply_text(
        f"<b>✅ Message Updated!</b>\n\n"
        f"📝 New message:\n<code>{new_message}</code>\n\n"
        f"Message akan digunakan untuk pengiriman berikutnya.",
        parse_mode='HTML'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command to show current configuration."""
    global custom_message
    
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    contacts = load_contacts()
    current_msg = custom_message if custom_message else STREAK_MESSAGE
    
    await update.message.reply_text(
        f"<b>📊 Bot Status</b>\n\n"
        f"⏰ <b>Schedule:</b> Daily at {SCHEDULE_TIME}\n"
        f"👥 <b>Contacts:</b> {len(contacts)}\n"
        f"📝 <b>Current Message:</b>\n<code>{current_msg}</code>\n\n"
        f"🎯 <b>Mode:</b> {'Headless' if HEADLESS_MODE else 'Visible Browser'}\n"
        f"✅ <b>Status:</b> Online & Active",
        parse_mode='HTML'
    )


async def run_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /run command - manually trigger the streak bot."""
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "<b>Running Streak Bot...</b>\n\n"
        "Please wait, this may take a minute.",
        parse_mode='HTML'
    )
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bot_script = os.path.join(script_dir, 'streak_bot.py')
        
        # Build command with custom message if set
        cmd = [sys.executable, bot_script, '--now']
        if custom_message:
            cmd.extend(['--message', custom_message])
        
        process = subprocess.Popen(
            cmd,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(timeout=300)
        
        if process.returncode == 0:
            await update.message.reply_text(
                "<b>Streak Bot Completed!</b>\n\n"
                "Check the notification for details.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"<b>Bot finished with errors</b>\n\n"
                f"Exit code: {process.returncode}",
                parse_mode='HTML'
            )
            
    except subprocess.TimeoutExpired:
        process.kill()
        await update.message.reply_text("Bot timed out after 5 minutes.")
    except Exception as e:
        await update.message.reply_text(f"Error running bot: {e}")


# =============================================================================
# Scheduler Thread
# =============================================================================

def run_scheduled_streak():
    """Run the streak bot (called by scheduler)."""
    logger.info(f"Scheduled job triggered at {SCHEDULE_TIME}")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bot_script = os.path.join(script_dir, 'streak_bot.py')
        
        # Build command with custom message if set
        cmd = [sys.executable, bot_script, '--now']
        if custom_message:
            cmd.extend(['--message', custom_message])
        
        process = subprocess.Popen(
            cmd,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(timeout=300)
        logger.info(f"Scheduled job completed with exit code: {process.returncode}")
        
    except Exception as e:
        logger.error(f"Scheduled job failed: {e}")


def scheduler_thread():
    """Background thread for running scheduled jobs."""
    logger.info(f"Scheduler started - will run daily at {SCHEDULE_TIME}")
    
    schedule.every().day.at(SCHEDULE_TIME).do(run_scheduled_streak)
    
    while True:
        schedule.run_pending()
        time.sleep(60)


# =============================================================================
# Main
# =============================================================================

def main():
    """Start the combined bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set in config.py")
        return
    
    print("="*60)
    print("TikTok Streak Bot - Combined")
    print("="*60)
    print(f"\nBot is running...")
    print(f"Authorized Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"Scheduled time: {SCHEDULE_TIME}")
    print(f"\nCommands available:")
    print("   /add {nickname}    - Add contact")
    print("   /remove {nickname} - Remove contact")
    print("   /list              - List contacts")
    print("   /run               - Run streak bot")
    print("\nPress Ctrl+C to stop\n")
    print("="*60)
    
    # Start scheduler in background thread
    scheduler = threading.Thread(target=scheduler_thread, daemon=True)
    scheduler.start()
    logger.info("Scheduler thread started")
    
    # Create Telegram application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_contact))
    application.add_handler(CommandHandler("remove", remove_contact))
    application.add_handler(CommandHandler("list", list_contacts))
    application.add_handler(CommandHandler("text", text_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("run", run_bot_command))
    
    # Send startup notification
    async def send_startup_message(app):
        contacts = load_contacts()
        await app.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=(
                "<b>TikTok Streak Bot Online!</b>\n\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Contacts: {len(contacts)}\n"
                f"Scheduled: {SCHEDULE_TIME} daily\n\n"
                "<b>Commands:</b>\n"
                "/add {nickname} - Add contact\n"
                "/remove {nickname} - Remove contact\n"
                "/list - Show contacts\n"
                "/run - Run streak bot"
            ),
            parse_mode='HTML'
        )
    
    application.post_init = send_startup_message
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
