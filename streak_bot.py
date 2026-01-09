"""
TikTok Streak Bot
==================
Automatically sends streak reminder messages to specified TikTok contacts.

Usage:
    python streak_bot.py           # Run bot (schedules at 7 AM daily)
    python streak_bot.py --now     # Send messages immediately
    python streak_bot.py --test    # Test mode (find contacts but don't send)
"""

import json
import sys
import time
import logging
import os
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions
import schedule
import requests

from config import (
    TIKTOK_MESSAGES_URL,
    STREAK_MESSAGE,
    SCHEDULE_TIME,
    COOKIES_FILE,
    CONTACTS_FILE,
    LOGS_DIR,
    HEADLESS_MODE,
    PAGE_LOAD_WAIT,
    ELEMENT_WAIT,
    MESSAGE_SEND_DELAY,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_ENABLED,
)


# Set up logging
def setup_logging():
    """Configure logging to both file and console."""
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


def send_telegram(message):
    """Send a message to Telegram."""
    if not TELEGRAM_ENABLED:
        return False
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.debug("Telegram not configured (missing token or chat_id)")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.debug("Telegram notification sent successfully")
            return True
        else:
            logger.warning(f"Telegram API error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"Failed to send Telegram notification: {e}")
        return False


class TikTokStreakBot:
    """Bot to automatically send streak messages on TikTok."""
    
    def __init__(self, headless=False, test_mode=False):
        """
        Initialize the TikTok Streak Bot.
        
        Args:
            headless: Run browser in headless mode
            test_mode: If True, find contacts but don't send messages
        """
        self.page = None
        self.headless = headless
        self.test_mode = test_mode
        self.target_usernames = []
        self.contacts_found = []
    
    def load_target_contacts(self):
        """Load target usernames from contacts.json file."""
        if not os.path.exists(CONTACTS_FILE):
            logger.error(f"Contacts file not found: {CONTACTS_FILE}")
            logger.error("Please create contacts.json with your target usernames.")
            return False
        
        try:
            with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.target_usernames = data.get('contacts', [])
            
            if not self.target_usernames:
                logger.warning("No contacts found in contacts.json")
                return False
            
            logger.info(f"📋 Loaded {len(self.target_usernames)} target contacts:")
            for username in self.target_usernames:
                logger.info(f"   - {username}")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in contacts.json: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading contacts: {e}")
            return False
    
    def create_browser(self):
        """Create a ChromiumPage browser instance with anti-detection settings."""
        options = ChromiumOptions()
        
        # Anti-detection settings
        options.set_argument('--disable-blink-features=AutomationControlled')
        options.set_argument('--disable-infobars')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--no-sandbox')
        
        # Headless mode
        if self.headless:
            options.set_argument('--headless=new')
        
        # Set a realistic user agent
        options.set_user_agent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = ChromiumPage(options)
        logger.info("Browser initialized successfully")
        return self.page
    
    def load_cookies(self):
        """Load cookies from file and apply to browser."""
        if not os.path.exists(COOKIES_FILE):
            logger.error(f"Cookies file not found: {COOKIES_FILE}")
            logger.error("Please export your TikTok cookies to cookies.json")
            return False
        
        try:
            with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # Navigate to TikTok first (cookies need a domain)
            self.page.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Add cookies
            for cookie in cookies:
                try:
                    self.page.set.cookies(cookie)
                except Exception as e:
                    logger.debug(f"Skipped cookie {cookie.get('name')}: {e}")
            
            logger.info(f"Loaded {len(cookies)} cookies")
            return True
            
        except Exception as e:
            logger.error(f"Error loading cookies: {e}")
            return False
    
    def verify_login(self):
        """Verify that we're logged in by checking the messages page."""
        try:
            self.page.get(TIKTOK_MESSAGES_URL)
            time.sleep(PAGE_LOAD_WAIT)
            
            current_url = self.page.url
            
            if 'login' in current_url:
                logger.error("Not logged in - redirected to login page")
                logger.error("Please run extract_cookies.py to refresh your cookies")
                return False
            
            if 'messages' in current_url:
                logger.info("✅ Login verified - on messages page")
                return True
            
            logger.warning(f"Unexpected URL: {current_url}")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying login: {e}")
            return False
    
    def find_target_contacts(self):
        """Find and match contacts from the message list with target nicknames."""
        self.contacts_found = []
        
        try:
            # Wait for conversation list to load
            time.sleep(ELEMENT_WAIT + 3)
            
            logger.info("Searching for contacts using TikTok nickname elements...")
            
            # First, try to find nickname elements using the specific TikTok class
            nickname_selectors = [
                'css:p[class*="PInfoNickname"]',
                'css:p[class*="Nickname"]',
                'css:span[class*="Nickname"]',
                'css:div[class*="Nickname"]',
            ]
            
            for target in self.target_usernames:
                found = False
                
                # Try each nickname selector
                for selector in nickname_selectors:
                    if found:
                        break
                    try:
                        nickname_elements = self.page.eles(selector)
                        logger.info(f"Found {len(nickname_elements)} elements with selector: {selector}")
                        
                        for elem in nickname_elements:
                            try:
                                elem_text = elem.text.strip() if elem.text else ""
                                logger.debug(f"  Checking nickname: '{elem_text}'")
                                
                                # Case-insensitive match
                                if elem_text.lower() == target.lower():
                                    # Find parent container to click
                                    parent = elem
                                    for _ in range(10):
                                        try:
                                            parent = parent.parent()
                                            if parent:
                                                parent_class = parent.attr('class') or ''
                                                # Look for conversation container
                                                if 'Item' in parent_class or 'item' in parent_class or 'Container' in parent_class:
                                                    self.contacts_found.append({
                                                        'element': parent,
                                                        'username': target,
                                                        'nickname_element': elem,
                                                        'index': len(self.contacts_found)
                                                    })
                                                    logger.info(f"✅ Found target contact: {target}")
                                                    found = True
                                                    break
                                        except:
                                            break
                                    
                                    # If we couldn't find a good parent, use the element itself
                                    if not found:
                                        self.contacts_found.append({
                                            'element': elem,
                                            'username': target,
                                            'nickname_element': elem,
                                            'index': len(self.contacts_found)
                                        })
                                        logger.info(f"✅ Found target (using element directly): {target}")
                                        found = True
                                    break
                            except Exception as e:
                                logger.debug(f"Error checking element: {e}")
                                continue
                    except Exception as e:
                        logger.debug(f"Error with selector {selector}: {e}")
                        continue
                
                # If still not found, try text search
                if not found:
                    try:
                        elem = self.page.ele(f'xpath://*[text()="{target}"]')
                        if not elem:
                            elem = self.page.ele(f'xpath://*[contains(text(), "{target}")]')
                        
                        if elem:
                            self.contacts_found.append({
                                'element': elem,
                                'username': target,
                                'index': len(self.contacts_found)
                            })
                            logger.info(f"✅ Found via text search: {target}")
                    except:
                        pass
            
            # Report results
            found_usernames = {c['username'].lower() for c in self.contacts_found}
            not_found = [u for u in self.target_usernames if u.lower() not in found_usernames]
            
            if not_found:
                logger.warning(f"⚠️ Could not find these contacts: {', '.join(not_found)}")
                # Show available nicknames for debugging
                logger.info("Available nicknames on this page:")
                try:
                    for selector in nickname_selectors:
                        elements = self.page.eles(selector)
                        for elem in elements[:10]:
                            if elem.text:
                                logger.info(f"  - {elem.text.strip()}")
                except:
                    pass
            
            logger.info(f"📊 Found {len(self.contacts_found)}/{len(self.target_usernames)} target contacts")
            return self.contacts_found
            
        except Exception as e:
            logger.error(f"Error finding contacts: {e}")
            return []
    
    def send_message(self, contact):
        """
        Send a streak message to a specific contact.
        
        Args:
            contact: Dictionary with contact info and element
        
        Returns:
            bool: True if message sent successfully
        """
        try:
            username = contact.get('username', 'Unknown')
            element = contact.get('element')
            
            logger.info(f"📤 Sending message to: {username}")
            
            # Click on the conversation to open it
            element.click()
            time.sleep(ELEMENT_WAIT)
            
            # Find the message input field
            input_field = self.page.ele('css:div[data-e2e="message-input"]')
            
            if not input_field:
                input_field = self.page.ele('css:div[contenteditable="true"]')
            
            if not input_field:
                input_field = self.page.ele('css:textarea[placeholder*="message"], input[placeholder*="message"]')
            
            if not input_field:
                input_field = self.page.ele('css:div[class*="Input"] div[contenteditable="true"]')
            
            if not input_field:
                logger.error(f"Could not find message input for {username}")
                return False
            
            # Click on input field to focus
            input_field.click()
            time.sleep(0.5)
            
            # Type the message
            input_field.input(STREAK_MESSAGE)
            time.sleep(0.5)
            
            # Find and click send button, or press Enter
            send_button = self.page.ele('css:button[data-e2e="send-button"], button[class*="send"], button[class*="Send"]')
            
            if send_button:
                send_button.click()
            else:
                # Press Enter to send
                input_field.input('\n')
            
            time.sleep(MESSAGE_SEND_DELAY)
            
            logger.info(f"✅ Message sent to: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {contact.get('username', 'Unknown')}: {e}")
            return False
    
    def send_all_messages(self):
        """Send messages to all found contacts."""
        if not self.contacts_found:
            logger.info("No contacts to message")
            return 0
        
        success_count = 0
        
        for contact in self.contacts_found:
            if self.test_mode:
                logger.info(f"[TEST MODE] Would send to: {contact.get('username')}")
                success_count += 1
            else:
                if self.send_message(contact):
                    success_count += 1
                # Small delay between messages
                time.sleep(1)
        
        logger.info(f"📊 Sent {success_count}/{len(self.contacts_found)} messages successfully")
        return success_count
    
    def run(self):
        """Main bot execution flow."""
        logger.info("="*60)
        logger.info("🚀 TikTok Streak Bot Starting")
        logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # Send start notification
        send_telegram("🚀 <b>TikTok Streak Bot Started</b>\n⏰ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        success_count = 0
        total_contacts = 0
        
        try:
            # Load target contacts from JSON
            if not self.load_target_contacts():
                send_telegram("❌ <b>Bot Error</b>\nFailed to load contacts from contacts.json")
                return False
            
            total_contacts = len(self.target_usernames)
            
            # Create browser
            self.create_browser()
            
            # Load cookies
            if not self.load_cookies():
                send_telegram("❌ <b>Bot Error</b>\nFailed to load cookies. Please update cookies.json")
                return False
            
            # Verify login
            if not self.verify_login():
                send_telegram("❌ <b>Bot Error</b>\nLogin failed. Cookies may have expired.")
                return False
            
            # Find target contacts in message list
            self.find_target_contacts()
            
            if not self.contacts_found:
                logger.info("No target contacts found in message list")
                send_telegram(f"⚠️ <b>No Contacts Found</b>\nCould not find any of the {total_contacts} target contacts in message list.")
                return True
            
            # Send messages
            success_count = self.send_all_messages()
            
            logger.info("="*60)
            logger.info("✅ Bot execution completed")
            logger.info("="*60)
            
            # Send success notification
            contact_list = "\n".join([f"  • {c['username']}" for c in self.contacts_found])
            send_telegram(
                f"✅ <b>Streak Messages Sent!</b>\n\n"
                f"📊 <b>Result:</b> {success_count}/{len(self.contacts_found)} successful\n\n"
                f"👥 <b>Contacts:</b>\n{contact_list}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            send_telegram(f"❌ <b>Bot Error</b>\n{str(e)}")
            return False
        
        finally:
            if self.page:
                self.page.quit()
                logger.info("Browser closed")
    
    def close(self):
        """Close the browser."""
        if self.page:
            self.page.quit()


def run_scheduled_job():
    """Job function for scheduled execution."""
    logger.info("⏰ Scheduled job triggered")
    bot = TikTokStreakBot(headless=HEADLESS_MODE)
    bot.run()


def main():
    """Main entry point."""
    # Parse command line arguments
    args = sys.argv[1:]
    
    if '--now' in args:
        # Run immediately
        logger.info("Running bot immediately (--now flag)")
        bot = TikTokStreakBot(headless=HEADLESS_MODE)
        bot.run()
        
    elif '--test' in args:
        # Test mode - find contacts but don't send
        logger.info("Running in test mode (--test flag)")
        bot = TikTokStreakBot(headless=False, test_mode=True)
        bot.run()
        
    else:
        # Schedule mode - run daily at configured time
        print("\n" + "="*60)
        print("🤖 TikTok Streak Bot")
        print("="*60)
        print(f"\n📅 Scheduled to run daily at: {SCHEDULE_TIME}")
        print(f"📝 Message: \"{STREAK_MESSAGE}\"")
        print(f"\n⏳ Waiting for scheduled time...")
        print("   Press Ctrl+C to stop\n")
        print("="*60 + "\n")
        
        # Schedule the job
        schedule.every().day.at(SCHEDULE_TIME).do(run_scheduled_job)
        
        logger.info(f"Next run scheduled at: {SCHEDULE_TIME}")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            print("\n👋 Bot stopped. Goodbye!")


if __name__ == "__main__":
    main()
