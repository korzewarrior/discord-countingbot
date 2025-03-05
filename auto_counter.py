import os
import json
import time
import random
import logging
import requests
import argparse
#import schedule
import datetime
import re
from threading import Thread
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_counter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutoCounter")

class DiscordAccount:
    """Represents a Discord user account for posting messages"""
    
    def __init__(self, username, user_token, user_agent=None):
        self.username = username
        self.token = user_token
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.last_used = None
        self.message_count = 0
        self.session = requests.Session()
        self.id = None  # Will be populated when we fetch account info
        
        # Set up default headers
        self.headers = {
            "Authorization": self.token,
            "User-Agent": self.user_agent,
            "Content-Type": "application/json"
        }
        
        # Try to get account ID
        self.get_account_info()
    
    def get_account_info(self):
        """Get account information including user ID"""
        try:
            url = "https://discord.com/api/v9/users/@me"
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.id = data.get('id')
                logger.info(f"Retrieved account info for {self.username}, ID: {self.id}")
                return True
            else:
                logger.error(f"Failed to get account info for {self.username}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error getting account info for {self.username}: {str(e)}")
            return False
    
    def send_message(self, channel_id, content):
        """Send a message to a Discord channel"""
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        
        payload = {
            "content": content,
            "tts": False
        }
        
        # Retry logic for network issues
        max_retries = 3
        retry_count = 0
        retry_delay = 1
        
        while retry_count < max_retries:
            try:
                response = self.session.post(url, headers=self.headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    self.last_used = datetime.datetime.now()
                    self.message_count += 1
                    logger.info(f"Message sent by {self.username}: {content}")
                    return True, response.json()
                elif response.status_code == 429:
                    # Handle rate limiting
                    try:
                        data = response.json()
                        retry_after = data.get('retry_after', 1)  # Default to 1 second if not specified
                        logger.warning(f"RATE LIMITED: Must wait {retry_after} seconds before next message")
                        return False, {"rate_limited": True, "retry_after": retry_after}
                    except:
                        logger.warning("Rate limited but couldn't parse response")
                        return False, {"rate_limited": True, "retry_after": 1}
                else:
                    logger.error(f"Failed to send message by {self.username}: {response.status_code} - {response.text}")
                    return False, f"HTTP Error: {response.status_code} - {response.text}"
            except requests.exceptions.Timeout:
                logger.error(f"Timeout when sending message by {self.username}")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {retry_count}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return False, "Network timeout after multiple retries"
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error when sending message by {self.username} - possibly network changed")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {retry_count}/{max_retries})")
                    # Recreate the session to handle network changes
                    self.session = requests.Session()
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return False, "Network connection error after multiple retries"
            except Exception as e:
                logger.error(f"Error sending message by {self.username}: {str(e)}")
                return False, f"Error: {str(e)}"
    
    def get_channel_messages(self, channel_id, limit=30):
        """Get messages from a Discord channel"""
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
        
        # Retry logic for network issues
        max_retries = 3
        retry_count = 0
        retry_delay = 1
        
        while retry_count < max_retries:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    messages = response.json()
                    # Ensure each message has at least the basic fields we need
                    for message in messages:
                        if 'content' not in message:
                            message['content'] = ''
                        if 'author' not in message:
                            message['author'] = {'username': 'unknown', 'id': '0'}
                        elif 'username' not in message['author']:
                            message['author']['username'] = 'unknown'
                    return messages
                else:
                    logger.error(f"Failed to get messages: {response.status_code} - {response.text}")
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"Retrying in {retry_delay} seconds... (attempt {retry_count}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        return []
            except requests.exceptions.Timeout:
                logger.error(f"Timeout when getting messages")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {retry_count}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return []
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error when getting messages - possibly network changed")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {retry_count}/{max_retries})")
                    # Recreate the session to handle network changes
                    self.session = requests.Session()
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return []
            except Exception as e:
                logger.error(f"Error getting messages: {str(e)}")
                return []
            
    def get_typing_delay(self, message_length):
        """Calculate a realistic typing delay for a message"""
        # For ultra-fast counting, we'll use minimal delays
        # This will be close to instant instead of simulating realistic typing
        return 0.05  # 50ms delay, barely noticeable
    
    def simulate_typing(self, channel_id, message_length):
        """Simulate typing indicator in a channel"""
        # Skip typing simulation in speed mode
        if hasattr(self, 'speed_mode') and self.speed_mode:
            return True
            
        url = f"https://discord.com/api/v9/channels/{channel_id}/typing"
        
        try:
            response = self.session.post(url, headers=self.headers)
            
            if response.status_code == 204:
                logger.debug(f"{self.username} is typing...")
                time.sleep(self.get_typing_delay(message_length))
                return True
            else:
                logger.error(f"Failed to trigger typing indicator: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error triggering typing: {str(e)}")
            return False


class AutoCounter:
    """Main class that manages automated counting in Discord"""
    
    def __init__(self, config_file="counter_config.json"):
        """Initialize the auto counter with configuration"""
        # Logger setup
        self.logger = logging.getLogger("AutoCounter")
        
        # Default configuration
        self.config_file = config_file
        self.accounts = []
        self.channel_id = None
        self.current_count = 0
        self.last_counter_index = None
        self.counting_active = False
        self.recovery_mode = False
        self.run_hours = (1, 5)  # Run between 1 AM and 5 AM by default
        self.min_delay = 1.0
        self.max_delay = 2.0
        self.jitter_factor = 0.2  # Random jitter to avoid patterns
        self.count_limit = None  # Maximum number of counts to perform (None = unlimited)
        self.counts_performed = 0  # Number of counts performed in current session
        self.scan_interval = 30  # How often to scan channel for updates (seconds)
        self.last_scan_time = 0  # When we last scanned the channel
        self.last_reset_time = 0  # Track when we last detected a reset
        self.bot_usernames = ["counting", "Counting", "CountingBot", "APP", "APP counting"]  # Common bot names to watch for
        self.speed_mode = False  # Ultra-fast counting mode
        self.messages_per_second = 5.0  # Default messages per second in speed mode
        self.verify_last_message = True  # Whether to verify the last message was received
        self.auto_restart_after_reset = False  # New flag for auto-restart after reset
        self.solo_mode = False  # New flag for solo mode - wait for external users to count
        self.last_external_counter = None  # Track the last external user who counted
        self.last_external_counter_id = None  # Track the last external user ID who counted
        self.last_counter_id = None  # Track the very last counter ID (whether bot or external user)
        self.solo_timeout = 300  # How long to wait for external users before counting anyway (5 minutes)
        self.last_external_count_time = 0  # When the last external user counted
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.channel_id = config.get('channel_id')
                self.current_count = config.get('current_count', 0)
                self.last_counter_index = config.get('last_counter_index')
                self.counting_active = config.get('counting_active', False)
                self.run_hours = tuple(config.get('run_hours', (1, 5)))
                self.min_delay = config.get('min_delay', 1.0)
                self.max_delay = config.get('max_delay', 2.0)
                self.count_limit = config.get('count_limit', None)
                self.bot_usernames = config.get('bot_usernames', self.bot_usernames)
                self.scan_interval = config.get('scan_interval', 30)
                self.speed_mode = config.get('speed_mode', False)
                self.messages_per_second = config.get('messages_per_second', 5.0)
                self.verify_last_message = config.get('verify_last_message', True)
                self.solo_mode = config.get('solo_mode', False)
                self.solo_timeout = config.get('solo_timeout', 300)
                self.last_external_counter = config.get('last_external_counter')
                self.last_external_counter_id = config.get('last_external_counter_id')
                self.last_counter_id = config.get('last_counter_id')
                self.last_external_count_time = config.get('last_external_count_time', 0)
                
                # Load accounts
                for account_data in config.get('accounts', []):
                    account = DiscordAccount(
                        account_data['username'],
                        account_data['token'],
                        account_data.get('user_agent')
                    )
                    account.message_count = account_data.get('message_count', 0)
                    self.accounts.append(account)
                    
                logger.info(f"Loaded configuration with {len(self.accounts)} accounts")
                logger.info(f"Current count: {self.current_count}")
                if self.solo_mode:
                    logger.info("Solo mode enabled - will wait for external users to count")
            else:
                logger.info("No configuration file found, creating new one")
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'channel_id': self.channel_id,
                'current_count': self.current_count,
                'last_counter_index': self.last_counter_index,
                'counting_active': self.counting_active,
                'run_hours': self.run_hours,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay,
                'count_limit': self.count_limit,
                'bot_usernames': self.bot_usernames,
                'scan_interval': self.scan_interval,
                'speed_mode': self.speed_mode,
                'messages_per_second': self.messages_per_second,
                'verify_last_message': self.verify_last_message,
                'solo_mode': self.solo_mode,
                'solo_timeout': self.solo_timeout,
                'last_external_counter': self.last_external_counter,
                'last_external_counter_id': self.last_external_counter_id,
                'last_counter_id': self.last_counter_id,
                'last_external_count_time': self.last_external_count_time,
                'accounts': []
            }
            
            # Save account data
            for account in self.accounts:
                account_data = {
                    'username': account.username,
                    'token': account.token,
                    'user_agent': account.user_agent,
                    'message_count': account.message_count
                }
                config['accounts'].append(account_data)
                
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            
    def add_account(self, username, token, user_agent=None):
        """Add a new Discord account"""
        for account in self.accounts:
            if account.token == token:
                logger.info(f"Account {username} already exists")
                return False
                
        account = DiscordAccount(username, token, user_agent)
        self.accounts.append(account)
        self.save_config()
        logger.info(f"Added account {username}")
        return True
        
    def remove_account(self, username):
        """Remove an account by username"""
        for i, account in enumerate(self.accounts):
            if account.username == username:
                self.accounts.pop(i)
                self.save_config()
                logger.info(f"Removed account {username}")
                return True
                
        logger.info(f"Account {username} not found")
        return False
        
    def set_channel(self, channel_id):
        """Set the Discord channel ID for counting"""
        self.channel_id = channel_id
        self.save_config()
        logger.info(f"Set channel ID to {channel_id}")
        return True
        
    def set_count_limit(self, limit):
        """Set the maximum number of counts to perform"""
        if limit is None or (isinstance(limit, int) and limit > 0):
            self.count_limit = limit
            self.save_config()
            logger.info(f"Set count limit to {limit}")
            return True
        else:
            logger.error(f"Invalid count limit: {limit}")
            return False
        
    def add_bot_username(self, bot_name):
        """Add a bot username to watch for"""
        if bot_name not in self.bot_usernames:
            self.bot_usernames.append(bot_name)
            self.save_config()
            logger.info(f"Added bot username: {bot_name}")
            return True
        return False
    
    def set_scan_interval(self, seconds):
        """Set how often to scan the channel for updates"""
        if isinstance(seconds, int) and seconds > 0:
            self.scan_interval = seconds
            self.save_config()
            logger.info(f"Set scan interval to {seconds} seconds")
            return True
        return False
    
    def toggle_speed_mode(self):
        """Toggle ultra-fast counting mode"""
        self.speed_mode = not self.speed_mode
        self.save_config()
        if self.speed_mode:
            logger.info(f"Speed mode ENABLED - counting at ~{self.messages_per_second} counts per second")
        else:
            logger.info("Speed mode DISABLED - using normal delays")
        return True
    
    def set_messages_per_second(self, count):
        """Set the number of messages to send per second in speed mode"""
        if not isinstance(count, (int, float)) or count <= 0:
            logger.error(f"Invalid messages per second: {count}. Must be a positive number.")
            return False
            
        # Add warning for extremely high values, but allow them
        if count > 50:
            logger.warning(f"LUDICROUS SPEED ACTIVATED: {count} messages per second may exceed Discord rate limits!")
        elif count > 20:
            logger.warning(f"VERY HIGH SPEED: {count} messages per second may risk Discord rate limiting")
        elif count > 10:
            logger.warning(f"HIGH SPEED: {count} messages per second - pushing Discord limits")
            
        self.messages_per_second = float(count)
        self.save_config()
        logger.info(f"Set speed to {self.messages_per_second} messages per second")
        return True
        
    def toggle_message_verification(self):
        """Toggle whether to verify the last message was received before sending next"""
        self.verify_last_message = not self.verify_last_message
        self.save_config()
        if self.verify_last_message:
            logger.info("Message verification ENABLED - will check last message before sending next")
        else:
            logger.info("Message verification DISABLED - will send at constant rate")
        return True
    
    def smart_speed(self):
        """Enable smart speed that automatically finds the optimal counting rate"""
        # Start more aggressively
        self.messages_per_second = 20.0
        self.speed_mode = True
        self.verify_last_message = False
        self.save_config()
        
        logger.info("SMART SPEED MODE ENABLED - Will automatically find optimal counting rate")
        logger.info("Starting at 20 messages per second and will adapt based on rate limits")
        return True
    
    def reset_count_to_one(self):
        """Reset the count to 1 and update state"""
        logger.warning("RESET: Resetting count to 1")
        
        # Update state
        self.current_count = 0  # Will be incremented to 1 on next count
        self.last_counter_index = None
        
        # Clear solo mode counters too
        self.last_counter_id = None
        self.last_external_counter = None
        self.last_external_counter_id = None
        self.last_external_count_time = 0
        
        # Save the updated state
        self.save_config()
        
        # Check if we need to auto-restart
        if self.counting_active and self.auto_restart_after_reset:
            logger.info("Auto-restart enabled, will restart counting")
            return "reset_auto_restart"
            
        return "reset"

    def auto_restart(self):
        """Automatically restart counting after a reset"""
        logger.warning("🔄 AUTO-RESTART: Restarting counting automatically after reset")
        
        # Make sure we're starting fresh
        self.current_count = 0
        self.last_counter_index = None
        self.counts_performed = 0
        
        # Set force reset to skip initial scan
        self.force_reset = True
        
        # Start counting again
        self.counting_active = True
        
        # Save config
        self.save_config()
        
        # Start a new counting thread
        self.counter_thread = Thread(target=self._counting_loop)
        self.counter_thread.daemon = True
        self.counter_thread.start()
        
        logger.info("✅ Auto-restart complete. Counting from 1 again...")
        return True
        
    def select_next_counter(self):
        """Select the next account to count"""
        # In solo mode, we always use the first account
        if self.solo_mode:
            if len(self.accounts) < 1:
                logger.error("Need at least 1 account for solo mode")
                return None
            return 0  # Always use the first account in solo mode
            
        # Standard mode requires at least 2 accounts
        if len(self.accounts) < 2:
            logger.error("Need at least 2 accounts to avoid counting twice in a row")
            return None
            
        # Filter out the last counter to avoid consecutive counts
        available_indices = [i for i in range(len(self.accounts)) if i != self.last_counter_index]
        
        if not available_indices:
            logger.error("No available accounts to use")
            return None
            
        # Select next counter
        next_index = random.choice(available_indices)
        logger.info(f"Selected next counter: {self.accounts[next_index].username}")
        return next_index
        
    def get_next_delay(self):
        """Calculate appropriate delay until next count"""
        # If speed mode is enabled, use ultra-fast delays
        if self.speed_mode:
            # Check if we're in ludicrous mode (>20 msgs/sec)
            if self.messages_per_second > 20:
                # In ludicrous mode, use minimal possible delay
                return 1.0 / self.messages_per_second * 0.95
                
            # Calculate delay based on configured messages per second
            base_delay = 1.0 / self.messages_per_second
            # Add minimal jitter to avoid exact patterns
            return base_delay * random.uniform(0.95, 1.05)
            
        # Otherwise use standard delay range
        min_delay = self.min_delay
        max_delay = self.max_delay
        
        # Add jitter to avoid predictable patterns
        jitter = random.uniform(1 - self.jitter_factor, 1 + self.jitter_factor)
        delay = random.uniform(min_delay, max_delay) * jitter
        
        return delay
        
    def check_run_hours(self):
        """Check if current hour is within run hours"""
        # If we're in test mode with a count limit, ignore run hours
        if self.count_limit is not None:
            return True
            
        current_hour = datetime.datetime.now().hour
        start_hour, end_hour = self.run_hours
        
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        else:  # Handle range that crosses midnight
            return current_hour >= start_hour or current_hour < end_hour
        
    def is_message_indicating_reset(self, content):
        """Check if a message indicates that the counting has been reset"""
        # Add better pattern matching for content for various reset formats
        content = content.lower()
        
        # Look for patterns that indicate the counting was reset
        reset_indicators = [
            r"next number is \*\*1\*\*",
            r"next number is 1",
            r"counting starts at 1",
            r"count starts.*?at 1",
            r"count starts.*?at \*\*1\*\*",
            r"ruined it at",
            r"ruined it at.*?next number is 1",  # Exact pattern from screenshot
            r"ruined it at.*?next number is.*?1",  # More flexible for the screenshot
            r"we reached \d+ before the streak ended",
            r"start again from 1",
            r"the.*?next.*?number.*?is.*?1",  # More flexible pattern
            r".*?ruined.*?at.*?\d+.*?next.*?number.*?is.*?1"  # Super flexible for any RUINED AT format
        ]
        
        # If any pattern matches, the message indicates a reset
        for pattern in reset_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"Reset detected with pattern: {pattern}")
                logger.warning(f"In message: {content}")
                return True
                
        # Special cases for APP counting bot
        if ("⚠️" in content and "1" in content) or ("ruined" in content and "1" in content):
            logger.warning(f"Reset detected with special case APP pattern in message: {content}")
            return True
        
        # Another backup check for APP's typical message format
        if "ruined" in content and "next number" in content:
            logger.warning(f"Reset detected with backup APP pattern in message: {content}")
            return True
            
        return False
        
    def scan_channel(self):
        """Scan the channel to determine the current count and who last counted
        Returns (success, message) tuple where success is a boolean and message contains info or error"""
        try:
            logger.info(f"Scanning channel {self.channel_id}")
            
            # Get the most recent messages (should be enough to determine the current state)
            messages = []
            for account in self.accounts:
                account_messages = account.get_channel_messages(self.channel_id, limit=30)
                if account_messages:
                    messages = account_messages
                    break
                    
            if not messages:
                return False, "No messages found in channel"
                
            # Track when we last scanned
            self.last_scan_time = time.time()
            
            # Only consider messages from the past 5 minutes for reset detection
            # This prevents the bot from reacting to old reset messages
            current_time = datetime.datetime.now().timestamp()
            recent_threshold = current_time - (5 * 60)  # 5 minutes ago
            
            # Initialize last_reset_time if it doesn't exist
            if not hasattr(self, 'last_reset_time'):
                self.last_reset_time = 0
                
            logger.info(f"Only considering reset messages newer than: {datetime.datetime.fromtimestamp(max(recent_threshold, self.last_reset_time)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # FIRST PHASE: Check for reset messages - this takes highest priority
            reset_detected = False
            latest_reset_time = 0
            
            # Process messages to find potential resets first
            # APP bot messages get highest priority
            for message in messages[:15]:  # Check more messages to be safe
                author_username = message.get("author", {}).get("username", "")
                content = message.get("content", "")
                
                # Get message timestamp (Discord format)
                timestamp_str = message.get("timestamp", "")
                message_time = 0
                
                # Parse timestamp if available
                if timestamp_str:
                    try:
                        # Convert ISO timestamp to datetime object
                        timestamp_dt = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        message_time = timestamp_dt.timestamp()
                    except (ValueError, TypeError):
                        message_time = 0
                
                # Skip old messages for reset detection
                if message_time < max(recent_threshold, self.last_reset_time):
                    logger.debug(f"Skipping old message: {content[:30]}... (from {datetime.datetime.fromtimestamp(message_time).strftime('%Y-%m-%d %H:%M:%S')})")
                    continue
                    
                # Direct check for APP bot messages about resets
                if author_username == "APP" or author_username == "APP counting" or author_username.upper() == "APP":
                    logger.info(f"Found APP bot message: {content}")
                    
                    # Specific checks for common APP reset messages
                    if "⚠️ The next number is" in content and "1" in content:
                        logger.warning(f"Reset detected from APP bot warning emoji message: {content}")
                        reset_detected = True
                        # Update latest reset time
                        if message_time > latest_reset_time:
                            latest_reset_time = message_time
                        
                    if "RUINED IT AT" in content or "ruined it at" in content.lower():
                        logger.warning(f"Reset detected from APP bot RUINED IT message: {content}")
                        reset_detected = True
                        # Update latest reset time
                        if message_time > latest_reset_time:
                            latest_reset_time = message_time
                            
                    # Add pattern matching the screenshot format
                    if "RUINED IT AT" in content and "Next number is" in content and "1" in content:
                        logger.warning(f"Reset detected from APP bot RUINED message with format: {content}")
                        reset_detected = True
                        # Update latest reset time
                        if message_time > latest_reset_time:
                            latest_reset_time = message_time
                            
                    # More generic reset detection for APP bots
                    if ("ruined" in content.lower() or "RUINED" in content) and ("1" in content or "one" in content.lower()):
                        logger.warning(f"Reset detected from APP bot with generic ruined pattern: {content}")
                        reset_detected = True
                        # Update latest reset time
                        if message_time > latest_reset_time:
                            latest_reset_time = message_time
            
            # If a reset was detected in this scan, update our reset time and reset the count
            if reset_detected:
                logger.warning(f"Reset detected during scan with timestamp {datetime.datetime.fromtimestamp(latest_reset_time).strftime('%Y-%m-%d %H:%M:%S')}")
                self.last_reset_time = latest_reset_time if latest_reset_time > 0 else current_time
                result = self.reset_count_to_one()
                # Check if we should auto-restart
                if result == "reset_auto_restart" and hasattr(self, 'auto_restart_after_reset') and self.auto_restart_after_reset:
                    # We're using auto_restart instead of returning immediate signal
                    # The counting loop will handle the restart
                    return True, "RESET_DETECTED_AUTO_RESTART"
                # Return special value to signal reset
                return True, "RESET_DETECTED_STOP_COUNTING"
            
            # SECOND PHASE: If we got here, no reset was detected, so find the latest count
            # Initialize variables to track our findings
            current_count = None
            last_counter = None
            last_counter_index = None
            most_recent_timestamp = 0
            most_recent_message_time = 0
            is_external_user = False  # Flag to track if the counter was an external user
            
            # Process the messages to find valid number sequences and the latest count
            for message in messages:
                author_username = message.get("author", {}).get("username", "")
                author_id = message.get("author", {}).get("id", "")
                content = message.get("content", "").strip()
                timestamp = message.get("timestamp", "")
                
                # Get message timestamp for checking against last reset
                message_time = 0
                if timestamp:
                    try:
                        # Convert ISO timestamp to datetime object
                        timestamp_dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        message_time = timestamp_dt.timestamp()
                    except (ValueError, TypeError):
                        message_time = 0
                
                # CRITICAL: Skip messages that came before the last reset
                # This ensures we don't pick up old counts from before a reset
                if message_time > 0 and message_time <= self.last_reset_time:
                    logger.debug(f"Skipping pre-reset message: {content} (from {datetime.datetime.fromtimestamp(message_time).strftime('%Y-%m-%d %H:%M:%S')})")
                    continue
                
                # Skip messages from counting bots (already processed above for reset detection)
                is_bot_message = False
                for bot_username in self.bot_usernames:
                    if bot_username.lower() in author_username.lower():
                        is_bot_message = True
                        break
                
                if is_bot_message:
                    continue
                    
                # THIS IS THE MISSING PART: Try to extract a number from the message
                try:
                    # If the content is a number, this could be a valid count
                    if content.isdigit():
                        number = int(content)
                        
                        # Update if this is the most recent valid count we've found
                        if message_time > most_recent_message_time:
                            current_count = number
                            last_counter = author_username
                            most_recent_message_time = message_time
                            
                            # Find which of our accounts this is (if any)
                            last_counter_index = None
                            for i, account in enumerate(self.accounts):
                                if account.username.lower() == author_username.lower():
                                    last_counter_index = i
                                    break
                                    
                            # Check if this is an external user
                            is_external_user = (last_counter_index is None)
                            
                            # IMPORTANT: Always track the last counter ID whether it's our bot or external user
                            if is_external_user:
                                # This is an external user
                                self.last_external_counter = author_username
                                self.last_external_counter_id = author_id
                                self.last_external_count_time = message_time
                                logger.info(f"External user {author_username} counted {number}")
                                self.last_counter_id = author_id  # Set the last counter ID directly
                            else:
                                # This is one of our bot accounts
                                if last_counter_index is not None:
                                    account_id = self.accounts[last_counter_index].id if hasattr(self.accounts[last_counter_index], 'id') else None
                                    if account_id:
                                        logger.info(f"Bot account {author_username} counted {number}")
                                        self.last_counter_id = account_id  # Set the last counter ID directly
                
                except (ValueError, TypeError):
                    continue
            
            # If we found a new reset, we should have returned earlier
            # Check if we're expecting to start from 1 (after a reset with no numbers yet)
            if self.current_count == 0 and current_count is None:
                logger.info("No new messages found after reset - keeping count at 0")
                return True, "Count is currently 0 (after reset)"
                            
            # If we found a valid count that's newer than the last reset, update our state
            if current_count is not None:
                logger.info(f"Scan results: Current count = {current_count}, last counter = {last_counter}, external user: {is_external_user}")
                
                # Update our internal state
                self.current_count = current_count
                self.last_counter_index = last_counter_index
                
                # If it's an external user, set the last_counter_id 
                # (this helps us track who last counted in solo mode)
                if is_external_user:
                    self.last_counter_id = self.last_external_counter_id
                
                self.save_config()
                
                # In solo mode, we want to know if a DIFFERENT external user counted
                if self.solo_mode and is_external_user:
                    return True, f"Current count: {current_count}, external user counted"
                
                return True, f"Current count: {current_count}"
            else:
                return False, "Could not determine current count from messages"
                
        except Exception as e:
            logger.error(f"Error scanning channel: {str(e)}")
            return False, f"Error scanning channel: {str(e)}"
            
    def verify_message_in_channel(self, expected_content):
        """Verify that a specific message exists in the channel"""
        if not self.verify_last_message:
            return True, "Message verification disabled"
            
        # Get most recent messages from channel
        account = self.accounts[0]
        success, response = account.get_channel_messages(self.channel_id, 5)
        
        if not success:
            logger.error(f"Failed to get messages for verification: {response}")
            return False, "Failed to get messages"
            
        messages = response
        if not messages:
            return False, "No messages found in channel"
            
        # Check if our expected message is in the most recent messages
        for msg in messages:
            content = msg.get('content', '').strip()
            if content == expected_content:
                return True, "Message verified in channel"
                
        logger.warning(f"Expected message '{expected_content}' not found in channel")
        return False, "Message not found"

    def start_counting(self, force_reset=False):
        """Start the counting process"""
        if self.counting_active:
            logger.warning("Counting is already active")
            return
            
        # Check if we need to set a new channel id
        if not self.channel_id:
            logger.error("Channel ID not set")
            return
        
        # ALWAYS force a reset to 0 if the current count in the config is 0
        # This ensures we always start from 1 after a reset
        if self.current_count == 0:
            logger.warning("Count is currently 0 (after reset) - forcing fresh start")
            force_reset = True
            # Make sure our internal state is properly reset
            self.current_count = 0
            self.last_counter_index = None
            self.save_config()
            
        # Set force reset flag for the counting loop to use
        if force_reset:
            self.force_reset = True
            logger.info("Force reset flag set - will skip initial scan and start counting immediately")
            # Update last_reset_time to now to prevent old messages from triggering resets
            self.last_reset_time = datetime.datetime.now().timestamp()
            logger.info(f"Set last_reset_time to current time to ignore old resets: {datetime.datetime.fromtimestamp(self.last_reset_time).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info("Performing direct scan before starting to ensure accurate count")
            scan_success, scan_message = self.scan_channel()
            
            if not scan_success:
                logger.error(f"Failed to scan channel: {scan_message}")
                return
                
            # CRITICAL: Check if scan detected a reset - if so, don't start counting
            if scan_message == "RESET_DETECTED_STOP_COUNTING" or "reset" in scan_message.lower():
                logger.warning(f"Reset detected during pre-start scan: {scan_message}")
                logger.warning("Cannot start counting after reset detection - use force option or menu option 16 to force start")
                return
        
        # Do a final config sanity check
        if self.current_count == 0:
            # We're starting after a reset, so make sure next number will be 1
            logger.info("Starting from scratch - next number will be 1")
            
        # Set the flag to start counting
        self.counting_active = True
        logger.info("Started counting")
        
        # If we have a count limit, log it
        if self.count_limit:
            logger.info(f"Will stop after {self.count_limit} counts")
            
        # Save the state
        self.save_config()
        
        # Start the counting thread
        self.counter_thread = Thread(target=self._counting_loop)
        self.counter_thread.daemon = True
        self.counter_thread.start()
        
    def stop_counting(self):
        """Stop the counting process"""
        self.counting_active = False
        self.save_config()
        logger.info(f"Stopped counting after {self.counts_performed} counts")
        return True
        
    def _counting_loop(self):
        """Main loop for automated counting"""
        last_message_content = None
        rate_limit_hits = 0
        consecutive_successes = 0
        
        # Set flag to skip first scan
        skip_first_scan = False
        
        # Check if we're in ludicrous mode
        ludicrous_mode = self.speed_mode and self.messages_per_second > 20
        if ludicrous_mode:
            logger.warning("LUDICROUS MODE ACTIVE - Disabling verification and minimizing operations for maximum speed!")
            logger.warning("Rate limiting may occur. Bot will automatically adjust speed if needed.")
        
        # Adaptive delay adjustment - with a maximum cap
        current_delay_modifier = 1.0
        MAX_DELAY_MODIFIER = 5.0  # Cap the maximum delay modifier to prevent excessive slowdown
        
        # Initialize auto-restart flag if it doesn't exist
        if not hasattr(self, 'auto_restart_after_reset'):
            self.auto_restart_after_reset = False
            
        # Watchdog timer for network issues
        last_successful_operation = time.time()
        network_watchdog_timeout = 60  # seconds before forcing a network reconnection
        
        # Initial scan to ensure we're starting with the correct count
        # Skip if force_reset is True
        if hasattr(self, 'force_reset') and self.force_reset:
            logger.info("Skipping initial scan due to force_reset flag")
            # Update last_reset_time to now to prevent old messages from triggering resets
            self.last_reset_time = datetime.datetime.now().timestamp()
            logger.info(f"Set last_reset_time to {self.last_reset_time} to ignore old resets")
            # Skip the first scan in the loop too
            skip_first_scan = True
            # Reset the flag after using it
            self.force_reset = False
        else:
            logger.info("Performing initial scan before starting counting loop")
            initial_scan_success, initial_scan_message = self.scan_channel()
            
            # If we're in solo mode, log who was the last counter for debugging
            if self.solo_mode:
                if self.last_counter_id:
                    # Check if the last counter was one of our accounts
                    is_our_account = False
                    for account in self.accounts:
                        if hasattr(account, 'id') and account.id == self.last_counter_id:
                            logger.warning(f"SOLO MODE: Last counter was our own account {account.username} - will wait for external user")
                            is_our_account = True
                            break
                    
                    if not is_our_account:
                        logger.info(f"SOLO MODE: Last counter was external user with ID {self.last_counter_id} - we can count next")
                else:
                    logger.warning("SOLO MODE: No last counter ID found - will proceed with counting")
            
            if not initial_scan_success:
                logger.error(f"Initial scan failed: {initial_scan_message}")
                logger.error("Cannot start counting without a valid initial scan")
                self.counting_active = False
                return
            # Check if initial scan detected a reset - if so, exit immediately
            if "reset" in initial_scan_message.lower():
                logger.warning(f"Count reset detected during initial scan: {initial_scan_message}")
                self.counting_active = False
                logger.warning("Counting loop terminated due to reset detection.")
                return
        
        # First loop iteration tracker
        first_loop = True
        
        while self.counting_active:
            try:
                # Check if we've reached our count limit
                if self.count_limit is not None and self.counts_performed >= self.count_limit:
                    logger.info(f"Reached count limit of {self.count_limit}, stopping")
                    self.counting_active = False
                    self.save_config()
                    break
                
                # ALWAYS scan for count resets - EXCEPT on first loop if skipping
                if not (first_loop and skip_first_scan):
                    logger.info("Scanning for potential count resets")
                    scan_success, scan_message = self.scan_channel()
                    
                    # If scan failed, wait and try again
                    if not scan_success:
                        logger.error(f"Scan failed: {scan_message}")
                        time.sleep(5)
                        continue
                        
                    # Check if scan detected a reset with auto-restart
                    if scan_message == "RESET_DETECTED_AUTO_RESTART":
                        logger.warning(f"Reset detected with auto-restart flag")
                        # Force-exit the loop
                        self.counting_active = False
                        self.save_config()  # Make sure config is saved
                        
                        # Wait 3 seconds before auto-restarting
                        logger.info("Waiting 3 seconds before auto-restart...")
                        time.sleep(3)
                        
                        # Auto-restart counting from 1
                        logger.warning("AUTO-RESTART: Starting fresh after reset")
                        self.auto_restart()
                        return
                    # Check if scan detected a reset - more robust detection of our special signal
                    elif scan_message == "RESET_DETECTED_STOP_COUNTING" or "reset" in scan_message.lower():
                        logger.warning(f"Reset detected during check: {scan_message}")
                        
                        # Check if auto-restart is enabled
                        if hasattr(self, 'auto_restart_after_reset') and self.auto_restart_after_reset:
                            logger.warning("CRITICAL: Reset detected! Automatically restarting...")
                            # Force-exit the loop
                            self.counting_active = False
                            self.save_config()  # Make sure config is saved
                            
                            # Wait 3 seconds before auto-restarting
                            logger.info("Waiting 3 seconds before auto-restart...")
                            time.sleep(3)
                            
                            # Auto-restart counting from 1
                            logger.warning("AUTO-RESTART: Starting fresh after reset")
                            self.auto_restart()
                            return
                        else:
                            # Traditional behavior - just stop
                            logger.warning("CRITICAL: Reset detected! Counting operation terminating.")
                            # Force-exit the loop
                            self.counting_active = False
                            self.save_config()  # Make sure config is saved
                            # Exit the loop
                            logger.warning("IMMEDIATE STOP: Exiting counting loop due to reset detection.")
                            return
                else:
                    logger.info("Skipping first loop scan when using force_reset")
                
                # After first loop, clear the first_loop flag
                first_loop = False
                
                # Skip run hour check in ludicrous mode
                if not ludicrous_mode:
                    # Check if we should be running right now
                    if not self.check_run_hours():
                        logger.info("Outside of run hours, waiting...")
                        time.sleep(60)  # Check every minute
                        continue
                
                # Double-check the next count is what we expect
                next_count = str(self.current_count + 1)
                logger.info(f"Planning to send count: {next_count}")
                
                # Select the next counter
                next_counter_index = self.select_next_counter()
                
                if next_counter_index is None:
                    logger.error("Failed to select next counter, waiting...")
                    time.sleep(10)
                    continue
                
                # Get the account to use
                next_account = self.accounts[next_counter_index]
                
                # Pass speed mode info to account
                if self.speed_mode:
                    next_account.speed_mode = True
                
                # SOLO MODE: Check if we should wait for an external user
                if self.solo_mode:
                    # In solo mode, we need to check if we were the last counter or an external user
                    current_time = time.time()
                    
                    # Calculate how long since the last external user counted
                    time_since_external = current_time - self.last_external_count_time if self.last_external_count_time > 0 else float('inf')
                    
                    # Get the ID of our bot account that will be counting
                    bot_account_id = None
                    for account in self.accounts:
                        if account.username == next_account.username:
                            bot_account_id = account.id if hasattr(account, 'id') else "bot_account"
                            break
                    
                    # The critical check: Simply check if the last counter was not this bot account
                    # (removing the unnecessary check against last_external_counter_id)
                    is_different_user = self.last_counter_id != bot_account_id
                    
                    if not is_different_user:
                        logger.info(f"Solo mode waiting: Need a different user to count. This bot account was the last counter.")
                        logger.info(f"Time since last external count: {time_since_external:.1f}s (timeout: {self.solo_timeout}s)")
                        time.sleep(5)  # Wait a bit before checking again
                        continue  # Skip counting this round
                    else:
                        logger.info(f"Solo mode: Different user has counted, proceeding with our count")
                
                # If not in solo mode, or if solo mode timeout expired, proceed with counting
                
                # Skip typing simulation in ludicrous mode
                if not ludicrous_mode:
                    # Optionally simulate typing before sending message
                    if hasattr(next_account, 'simulate_typing') and callable(getattr(next_account, 'simulate_typing')):
                        # Simulate typing
                        next_account.simulate_typing(self.channel_id, len(next_count))
                
                # FINAL check before sending to make sure count hasn't changed
                final_check_success, _ = self.scan_channel()
                next_count = str(self.current_count + 1)  # Recalculate in case scan updated the count
                
                # Send the count
                success, response = next_account.send_message(self.channel_id, next_count)
                
                if success:
                    # Update state
                    self.current_count += 1
                    self.last_counter_index = next_counter_index
                    self.counts_performed += 1
                    last_message_content = next_count  # Store for verification
                    
                    # Update the last counter ID to the bot account that just counted
                    if hasattr(next_account, 'id') and next_account.id:
                        self.last_counter_id = next_account.id
                    
                    # Successful message, track consecutive successes
                    consecutive_successes += 1
                    
                    # Faster speed increases - if we've had 5 successful messages, try reducing the delay modifier
                    if consecutive_successes >= 5 and current_delay_modifier > 1.0:
                        current_delay_modifier = max(1.0, current_delay_modifier * 0.8)  # Decrease delay by 20%
                        logger.info(f"Speed increased! Current delay modifier: {current_delay_modifier:.2f}x")
                        consecutive_successes = 0
                    
                    # In ludicrous mode, save config very rarely for maximum speed
                    if ludicrous_mode:
                        if self.counts_performed % 100 == 0:
                            self.save_config()
                    # In speed mode, only save config every 10 counts to improve performance
                    elif not self.speed_mode or self.counts_performed % 10 == 0:
                        self.save_config()
                    
                    # Log progress (less frequently in ludicrous mode)
                    if ludicrous_mode:
                        if self.counts_performed % 50 == 0:
                            logger.info(f"LUDICROUS COUNT: {self.current_count} | Progress: {self.counts_performed}/{self.count_limit if self.count_limit else 'unlimited'}")
                    elif not self.speed_mode or self.counts_performed % 5 == 0:
                        logger.info(f"Count: {self.current_count} | By: {next_account.username} | "
                                  f"Progress: {self.counts_performed}/{self.count_limit if self.count_limit else 'unlimited'}")
                    
                    # Calculate delay for next count with adaptive adjustment
                    base_delay = self.get_next_delay()
                    adjusted_delay = base_delay * current_delay_modifier
                    
                    if not ludicrous_mode and (not self.speed_mode or self.counts_performed % 5 == 0):
                        logger.info(f"Next count in {adjusted_delay:.2f} seconds")
                        
                    # Wait before sending the next count
                    time.sleep(adjusted_delay)
                else:
                    # Message failed
                    logger.error(f"Failed to send message: {response}")
                    
                    # Check for rate limiting
                    if isinstance(response, dict) and response.get('rate_limited'):
                        # Handle dictionary response from our rate limit handling
                        rate_limit_hits += 1
                        consecutive_successes = 0
                        
                        # Extract the required wait time
                        retry_after = float(response.get('retry_after', 1.0))
                        
                        # Add some extra cushion
                        retry_after += 0.5
                        
                        # Increase delay modifier after rate limit hit
                        if current_delay_modifier < MAX_DELAY_MODIFIER:
                            current_delay_modifier = min(MAX_DELAY_MODIFIER, current_delay_modifier * 1.5)
                            
                        # Log warning
                        logger.warning(f"Rate limited! Waiting {retry_after} seconds. Delay multiplier now {current_delay_modifier:.2f}x")
                        
                        # If we're getting a lot of rate limits, reduce the message rate
                        if rate_limit_hits >= 3 and self.speed_mode:
                            original_rate = self.messages_per_second
                            self.messages_per_second = max(0.5, self.messages_per_second * 0.7)  # Reduce by 30%
                            logger.warning(f"Too many rate limits! Reducing message rate from {original_rate:.1f} to {self.messages_per_second:.1f} per second")
                            rate_limit_hits = 0
                            self.save_config()
                            
                        # Wait the required time before trying again
                        time.sleep(retry_after)
                    elif isinstance(response, str) and "rate limited" in response.lower():
                        # Handle string response containing rate limit info
                        rate_limit_hits += 1
                        consecutive_successes = 0
                        
                        # Default retry time
                        retry_after = 1.0
                        
                        # Try to extract retry time from response
                        try:
                            retry_after_match = re.search(r"retry_after: (\d+\.?\d*)", response)
                            if retry_after_match:
                                retry_after = float(retry_after_match.group(1))
                        except Exception as e:
                            logger.error(f"Error parsing retry_after from response: {e}")
                        
                        # Add some extra cushion
                        retry_after += 0.5
                        
                        # Increase delay modifier after rate limit hit
                        if current_delay_modifier < MAX_DELAY_MODIFIER:
                            current_delay_modifier = min(MAX_DELAY_MODIFIER, current_delay_modifier * 1.5)
                            
                        # Log warning
                        logger.warning(f"Rate limited! Waiting {retry_after} seconds. Delay multiplier now {current_delay_modifier:.2f}x")
                        
                        # If we're getting a lot of rate limits, reduce the message rate
                        if rate_limit_hits >= 3 and self.speed_mode:
                            original_rate = self.messages_per_second
                            self.messages_per_second = max(0.5, self.messages_per_second * 0.7)  # Reduce by 30%
                            logger.warning(f"Too many rate limits! Reducing message rate from {original_rate:.1f} to {self.messages_per_second:.1f} per second")
                            rate_limit_hits = 0
                            self.save_config()
                            
                        # Wait the required time before trying again
                        time.sleep(retry_after)
                    elif "network timeout" in str(response).lower() or "connection error" in str(response).lower():
                        # Handle network issues
                        logger.warning(f"Network issue detected: {response}")
                        logger.warning("Waiting before retry to allow network to recover...")
                        time.sleep(5)  # Give network time to recover
                        
                        # Check if we've been having network issues for too long
                        if time.time() - last_successful_operation > network_watchdog_timeout:
                            logger.warning("Network watchdog triggered! Resetting network connections.")
                            # Reset connections for all accounts
                            for acc in self.accounts:
                                acc.session = requests.Session()
                            last_successful_operation = time.time()  # Reset the timer
                    else:
                        # Some other error, wait a bit before continuing
                        logger.error("Message failed for a reason other than rate limiting")
                        time.sleep(5)
            except Exception as e:
                logger.error(f"Error in counting loop: {str(e)}")
                logger.error(f"Full exception details: {traceback.format_exc()}")
                # If we get an exception, wait a moment before continuing
                time.sleep(5)
                
                # Check if we're having persistent issues
                if time.time() - last_successful_operation > network_watchdog_timeout:
                    logger.warning("Error watchdog triggered! Resetting connections and restarting loop.")
                    # Reset all connections
                    for acc in self.accounts:
                        acc.session = requests.Session()

    def fix_count_mismatch(self):
        """Emergency method to check and fix count mismatches directly from current messages"""
        try:
            logger.warning("EMERGENCY COUNT FIX: Checking for count mismatches")
            
            # Get the most recent messages
            messages = []
            for account in self.accounts:
                account_messages = account.get_channel_messages(self.channel_id, limit=10)
                if account_messages:
                    messages = account_messages
                    break
                    
            if not messages:
                logger.error("No messages found to fix count mismatch")
                return False
                
            # First, check for reset messages in the most recent messages
            for message in messages[:10]:
                author_username = message.get("author", {}).get("username", "")
                content = message.get("content", "")
                
                # Check if this is from APP or other counting bot
                is_bot_message = False
                for bot_username in self.bot_usernames:
                    if bot_username.lower() in author_username.lower():
                        is_bot_message = True
                        break
                        
                if is_bot_message and ("next number is 1" in content.lower() or "⚠️" in content):
                    logger.warning(f"Found reset message: {content}")
                    self.reset_count_to_one()
                    return True
                    
            # If no reset message, find the most recent number
            for message in messages:
                author_username = message.get("author", {}).get("username", "")
                content = message.get("content", "").strip()
                
                # Skip bot messages
                is_bot_message = False
                for bot_username in self.bot_usernames:
                    if bot_username.lower() in author_username.lower():
                        is_bot_message = True
                        break
                        
                if is_bot_message:
                    continue
                    
                # Try to extract a number
                try:
                    number = int(content)
                    logger.warning(f"Found most recent count: {number} from {author_username}")
                    
                    # Update our state
                    self.current_count = number
                    
                    # Find account index
                    for i, account in enumerate(self.accounts):
                        if account.username.lower() == author_username.lower():
                            self.last_counter_index = i
                            break
                            
                    self.save_config()
                    return True
                    
                except (ValueError, TypeError):
                    continue
                    
            logger.error("Could not find a valid count to fix mismatch")
            return False
            
        except Exception as e:
            logger.error(f"Error fixing count mismatch: {str(e)}")
            return False
            
    def reconnect_all_sessions(self):
        """Reset all network sessions when a network change is detected"""
        logger.warning("Network change detected! Reconnecting all sessions...")
        try:
            # Preserve account IDs during reconnection
            for account in self.accounts:
                try:
                    # Save the current ID before recreating session
                    account_id = account.id if hasattr(account, 'id') else None
                    
                    # Close existing session if possible
                    if hasattr(account.session, 'close'):
                        account.session.close()
                    # Create new session
                    account.session = requests.Session()
                    
                    # Restore the account ID if it existed
                    if account_id:
                        account.id = account_id
                        
                    logger.info(f"Reconnected session for account: {account.username}")
                except Exception as e:
                    logger.error(f"Error reconnecting session for account {account.username}: {str(e)}")
                    
            # Force a scan after reconnection to ensure we have the latest state
            logger.info("Running scan after reconnection to ensure latest state...")
            self.scan_channel()
            
            logger.info("All sessions reconnected successfully")
            return True
        except Exception as e:
            logger.error(f"Error in reconnect_all_sessions: {str(e)}")
            return False

    def force_rescan_for_resets(self):
        """Force a deep rescan of the channel specifically looking for reset messages"""
        logger.warning("EMERGENCY: Performing deep rescan for reset messages")
        
        try:
            # Get the most recent messages (more than usual to really check)
            messages = []
            for account in self.accounts:
                account_messages = account.get_channel_messages(self.channel_id, limit=50)  # Scan more messages
                if account_messages:
                    messages = account_messages
                    break
                    
            if not messages:
                logger.error("No messages found in channel during deep rescan")
                return False, "No messages found"
            
            # Temporarily disable time-based filtering to catch all reset messages
            original_reset_time = self.last_reset_time
            self.last_reset_time = 0
            
            # Scan for reset messages from bots
            for message in messages:
                author_username = message.get("author", {}).get("username", "")
                content = message.get("content", "")
                
                # First check if this is a bot message
                is_bot_message = False
                for bot_username in self.bot_usernames:
                    if bot_username.lower() in author_username.lower():
                        is_bot_message = True
                        break
                
                # Check APP bot specifically
                is_app_bot = author_username == "APP" or author_username.upper() == "APP" or author_username == "APP counting"
                
                if is_bot_message or is_app_bot:
                    # Check for reset indicators in a more aggressive way
                    if "ruined" in content.lower() or "reset" in content.lower() or "next number is 1" in content.lower():
                        logger.warning(f"Found reset message: {content} from {author_username}")
                        
                        # Reset the count
                        self.reset_count_to_one()
                        
                        # Restore the original reset time but add this one
                        timestamp_str = message.get("timestamp", "")
                        if timestamp_str:
                            try:
                                timestamp_dt = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                self.last_reset_time = timestamp_dt.timestamp()
                                logger.info(f"Updated last_reset_time to {datetime.datetime.fromtimestamp(self.last_reset_time).strftime('%Y-%m-%d %H:%M:%S')}")
                            except (ValueError, TypeError):
                                self.last_reset_time = datetime.datetime.now().timestamp()
                        else:
                            self.last_reset_time = datetime.datetime.now().timestamp()
                            
                        return True, "Reset detected and count set to 0"
            
            # If we get here, no reset was found
            self.last_reset_time = original_reset_time
            logger.info("No reset messages found during deep rescan")
            return False, "No reset messages found"
            
        except Exception as e:
            logger.error(f"Error during deep rescan: {str(e)}")
            return False, f"Error during deep rescan: {str(e)}"

def display_menu():
    """Display menu options and return user choice"""
    print("\n=== Discord Auto Counter ===")
    print("1. Add Account")
    print("2. Remove Account")
    print("3. List Accounts")
    print("4. Set Channel")
    print("5. Configure Settings")
    print("6. Set Count Limit (Test Mode)")
    print("7. Scan Channel Now")
    print("8. Start Counting")
    print("9. Stop Counting")
    print("10. Show Status")
    print("11. Toggle Speed Mode")
    print("12. Configure Speed")
    print("13. Toggle Message Verification")
    print("14. LUDICROUS SPEED")
    print("15. SMART SPEED (Auto-Adjust)")
    print("16. Force Start (Skip Initial Scan)")
    print("17. EMERGENCY: Fix Count Mismatch")
    print("18. Toggle Auto-Restart After Reset")
    print("19. NETWORK: Reconnect All Sessions")
    print("20. Toggle Solo Mode")
    print("21. Configure Solo Timeout (Legacy - Not Used)")
    print("22. EMERGENCY: Force Reset Count to 1")
    print("23. EMERGENCY: Deep Scan for Reset Messages")
    print("0. Exit")
    
    return input("Select an option: ")

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Discord Auto Counter Bot')
    parser.add_argument('--start', action='store_true', help='Start counting immediately')
    parser.add_argument('--force', action='store_true', help='Skip initial scan and use current count')
    parser.add_argument('--fix', action='store_true', help='Run emergency count mismatch fix')
    parser.add_argument('--version', action='store_true', help='Show bot version and exit')
    parser.add_argument('--auto-restart', action='store_true', help='Enable auto-restart after resets')
    parser.add_argument('--smart-speed', action='store_true', help='Enable smart speed adjustment')
    parser.add_argument('--reconnect', action='store_true', help='Reconnect all network sessions')
    parser.add_argument('--solo', action='store_true', help='Enable solo mode - wait for external users')
    args = parser.parse_args()
    
    # Load configuration
    counter = AutoCounter()
    
    if args.version:
        print("Discord Auto Counter v1.5.0")
        return

    if args.fix:
        print("=== EMERGENCY COUNT FIX ===")
        counter.fix_count_mismatch()
        return
        
    # Reconnect network sessions if specified
    if args.reconnect:
        print("=== RECONNECTING NETWORK SESSIONS ===")
        counter.reconnect_all_sessions()
        
    # Set auto-restart flag if specified
    if args.auto_restart:
        counter.auto_restart_after_reset = True
        logger.info("🔄 Auto-restart enabled: Bot will automatically restart after resets")
        
    # Enable smart speed if specified
    if args.smart_speed:
        counter.smart_speed()
        logger.info("🧠 Smart speed mode enabled: Bot will adjust speed automatically")
        
    # Enable solo mode if specified
    if args.solo:
        counter.solo_mode = True
        counter.save_config()
        logger.info("👤 Solo mode enabled: Bot will wait for external users to count")
        
    # Start immediately if specified
    if args.start:
        counter.start_counting(force_reset=args.force)
        
    # Main menu loop
    while True:
        choice = display_menu()
        
        if choice == '1':
            # Add account
            username = input("Enter Discord username: ")
            token = input("Enter account token: ")
            user_agent = input("Enter user agent (optional, press Enter to use default): ")
            
            if not user_agent:
                user_agent = None
                
            counter.add_account(username, token, user_agent)
            print(f"✅ Account {username} added successfully")
            
        elif choice == '2':
            username = input("Enter username to remove: ")
            if counter.remove_account(username):
                print(f"Removed account {username}")
            else:
                print(f"Failed to remove account {username}")
                
        elif choice == '3':
            accounts = counter.accounts
            print("\n=== Accounts ===")
            for i, account in enumerate(accounts):
                print(f"{i+1}. {account.username}")
            print(f"Total: {len(accounts)} accounts")
            
        elif choice == '4':
            channel_id = input("Enter Discord channel ID: ")
            counter.set_channel(channel_id)
            print(f"Set channel ID to {channel_id}")
            
        elif choice == '5':
            settings_choice = input("\nSettings:\n1. Set Min Delay\n2. Set Max Delay\n3. Set Run Hours\n4. Add Bot Username\n5. Set Scan Interval\n6. Back\nSelect a setting: ")
            
            if settings_choice == '1':
                min_delay = float(input("Enter minimum delay (seconds): "))
                counter.min_delay = min_delay
                counter.save_config()
                print(f"Set minimum delay to {min_delay} seconds")
                
            elif settings_choice == '2':
                max_delay = float(input("Enter maximum delay (seconds): "))
                counter.max_delay = max_delay
                counter.save_config()
                print(f"Set maximum delay to {max_delay} seconds")
                
            elif settings_choice == '3':
                start_hour = int(input("Enter start hour (0-23): "))
                end_hour = int(input("Enter end hour (0-23): "))
                counter.run_hours = (start_hour, end_hour)
                counter.save_config()
                print(f"Set run hours to {start_hour}-{end_hour}")
                
            elif settings_choice == '4':
                bot_name = input("Enter bot username to track: ")
                counter.add_bot_username(bot_name)
                print(f"Added bot username: {bot_name}")
                
            elif settings_choice == '5':
                interval = int(input("Enter scan interval (seconds): "))
                counter.set_scan_interval(interval)
                print(f"Set scan interval to {interval} seconds")
                
        elif choice == '6':
            limit_input = input("Enter count limit (or 'none' for unlimited): ")
            if limit_input.lower() == 'none':
                counter.set_count_limit(None)
                print("Count limit removed (unlimited)")
            else:
                try:
                    limit = int(limit_input)
                    counter.set_count_limit(limit)
                    print(f"Set count limit to {limit}")
                except ValueError:
                    print("Invalid limit. Please enter a number or 'none'")
                    
        elif choice == '7':
            print("\n=== Scanning Channel ===")
            print("Scanning channel for current count...")
            success, message = counter.scan_channel()
            if success:
                print(f"✅ Scan successful: {message}")
            else:
                print(f"❌ Scan failed: {message}")
            print(f"Current count is {counter.current_count}, next number should be {counter.current_count + 1}")
            
        elif choice == '8':
            if counter.start_counting():
                print("Started counting")
                print(f"Will stop after {counter.count_limit} counts" if counter.count_limit else "Will count indefinitely")
            else:
                print("Failed to start counting")
                
        elif choice == '9':
            counter.stop_counting()
            print("Stopped counting")
            
        elif choice == '10':
            print("\n=== Status ===")
            print(f"Current count: {counter.current_count}")
            print(f"Next count: {counter.current_count + 1}")
            print(f"Counting active: {counter.counting_active}")
            print(f"Speed mode: {counter.speed_mode}")
            print(f"Messages per second: {counter.messages_per_second}")
            print(f"Message verification: {counter.verify_last_message}")
            print(f"Count limit: {counter.count_limit if counter.count_limit else 'unlimited'}")
            print(f"Solo mode: {counter.solo_mode}")
            if counter.solo_mode:
                print(f"Solo timeout: {counter.solo_timeout} seconds (Note: This value is not actually used)")
            if counter.last_external_counter:
                print(f"Last external counter: {counter.last_external_counter}")
                time_since = time.time() - counter.last_external_count_time if counter.last_external_count_time > 0 else float('inf')
                print(f"Time since external count: {int(time_since)} seconds")
            if counter.last_counter_id:
                print(f"Last counter ID: {counter.last_counter_id}")
                # Check if our bot was the last counter
                is_bot_last_counter = False
                for account in counter.accounts:
                    if hasattr(account, 'id') and account.id == counter.last_counter_id:
                        is_bot_last_counter = True
                        break
                print(f"Last counter was {'our bot' if is_bot_last_counter else 'an external user'}")
            if counter.last_counter_index is not None:
                print(f"Last counter: {counter.accounts[counter.last_counter_index].username}")
            
        elif choice == '11':
            counter.toggle_speed_mode()
            print(f"Speed mode {'enabled' if counter.speed_mode else 'disabled'}")
            
        elif choice == '12':
            speed = float(input("Enter messages per second: "))
            counter.set_messages_per_second(speed)
            print(f"Set speed to {speed} messages per second")
            
        elif choice == '13':
            counter.toggle_message_verification()
            print(f"Message verification {'enabled' if counter.verify_last_message else 'disabled'}")
            
        elif choice == '14':
            counter.set_messages_per_second(50.0)
            if not counter.speed_mode:
                counter.toggle_speed_mode()
            print("🚀 LUDICROUS SPEED ENGAGED!")
            print("⚠️ Warning: This may trigger Discord rate limits")
            
        elif choice == '15':
            counter.smart_speed()
            print("🧠 SMART SPEED ACTIVATED")
            print("Will start at 20 messages per second and adjust as needed")
        
        elif choice == '16':
            counter.start_counting(force_reset=True)
            print("Forced start - skipping initial scan")
            
        elif choice == '17':
            print("\n=== EMERGENCY COUNT FIX ===")
            counter.fix_count_mismatch()
            
        elif choice == '18':
            # Toggle auto-restart
            if hasattr(counter, 'auto_restart_after_reset') and counter.auto_restart_after_reset:
                counter.auto_restart_after_reset = False
                print("❌ Auto-restart DISABLED")
            else:
                counter.auto_restart_after_reset = True
                print("✅ Auto-restart ENABLED - Bot will automatically restart after resets")
            
        elif choice == '19':
            # Reconnect all network sessions
            print("=== RECONNECTING NETWORK SESSIONS ===")
            if counter.reconnect_all_sessions():
                print("✅ All network sessions reconnected successfully")
            else:
                print("❌ Error reconnecting network sessions")
            
        elif choice == '20':
            # Toggle solo mode
            if counter.solo_mode:
                counter.solo_mode = False
                print("❌ Solo mode DISABLED")
            else:
                counter.solo_mode = True
                print("✅ Solo mode ENABLED - Bot will wait for external users")
            
        elif choice == '21':
            print("⚠️ NOTE: Solo timeout is no longer used. Bot will always wait for another user when in solo mode.")
            print("This option is kept for compatibility but has no effect.")
            timeout = int(input("Enter solo timeout (seconds): "))
            counter.solo_timeout = timeout
            counter.save_config()
            print(f"Set solo timeout to {timeout} seconds (Note: This value is not actually used)")
            
        elif choice == '22':
            print("\n=== EMERGENCY COUNT FIX ===")
            counter.reset_count_to_one()
            
        elif choice == '23':
            print("\n=== EMERGENCY: Deep Scan for Reset Messages ===")
            success, message = counter.force_rescan_for_resets()
            if success:
                print(f"✅ Reset detected and count set to 0: {message}")
            else:
                print(f"❌ Reset detection failed: {message}")
            
        elif choice == '0':
            print("Exiting...")
            break
            
        else:
            print("Invalid option")
            
if __name__ == "__main__":
    main() 