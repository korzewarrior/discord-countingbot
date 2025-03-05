# Discord Auto Counter - Technical Implementation Details

## Code Structure

### DiscordAccount Class
This class represents a single Discord user account and provides methods to interact with Discord's API:

```python
class DiscordAccount:
    def __init__(self, username, user_token, user_agent=None):
        # Initialize account with credentials
        
    def send_message(self, channel_id, content):
        # Send message to Discord channel
        
    def get_channel_messages(self, channel_id, limit=30):
        # Retrieve messages from Discord channel
        
    def simulate_typing(self, channel_id, message_length):
        # Send typing indicator to channel
```

Key implementation details:
- Uses Discord's REST API directly instead of official libraries
- Handles rate limiting through response code detection
- Implements retry logic for network resilience
- Creates and maintains HTTP sessions for persistent connections

### AutoCounter Class
This class manages the core counting logic and coordinates accounts:

```python
class AutoCounter:
    def __init__(self, config_file="counter_config.json"):
        # Initialize with configuration
        
    def scan_channel(self):
        # Scan channel to determine current count
        
    def reset_count_to_one(self):
        # Handle count reset
        
    def auto_restart(self):
        # Automatically restart counting after reset
        
    def _counting_loop(self):
        # Main loop for automated counting
        
    def fix_count_mismatch(self):
        # Emergency fix for count issues
```

Key implementation details:
- Two-phase scanning: reset detection followed by count detection
- Timestamp tracking to filter old reset messages
- Exponential backoff for rate limit handling
- Network watchdog to detect and fix connection issues

## Critical Algorithms

### Count Scanning Algorithm
1. Retrieve recent messages from the channel (up to 30)
2. First phase: Scan for reset messages from counting bots
   - Check for reset patterns like "next number is 1"
   - Check timestamp to only consider recent messages
   - If reset detected, immediately halt and restart
3. Second phase: If no reset, scan for numeric messages
   - Filter out bot messages
   - Extract numeric content
   - Determine highest valid count
   - Identify who sent the last count

### Reset Detection Algorithm
Reset messages are detected using pattern matching:
```python
def is_message_indicating_reset(self, content):
    """Check if a message indicates a count reset"""
    reset_patterns = [
        r"next number is \*\*1\*\*",
        r"next number is 1",
        r"ruined .* at .* next number is 1",
        r"Next number is \*\*1\*\*",
        r"RUINED IT AT .* Next number is \*\*1\*\*"
    ]
    
    for pattern in reset_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            logger.warning(f"Reset detected with pattern: {pattern}")
            logger.warning(f"In message: {content}")
            return True
            
    return False
```

### Account Selection Algorithm
The bot alternates between accounts to avoid Discord's rate limits:
```python
def select_next_counter(self):
    """Select the next account to post a count"""
    if not self.accounts:
        return None
        
    if self.last_counter_index is None:
        return 0
        
    # Simple round-robin selection
    next_index = (self.last_counter_index + 1) % len(self.accounts)
    return next_index
```

### Adaptive Speed Control
The bot dynamically adjusts its speed based on rate limit responses:
1. Start with configured messages per second
2. Track successful messages and rate limit hits
3. Increase speed after consecutive successes
4. Decrease speed after rate limit hits
5. Apply exponential backoff when needed

## Network Resilience Implementation

The bot includes sophisticated network resilience features:

1. **Retry Logic**: Automatically retries failed requests
   ```python
   max_retries = 3
   retry_count = 0
   retry_delay = 1
   
   while retry_count < max_retries:
       try:
           # Make request
       except requests.exceptions.ConnectionError:
           # Handle connection error
           retry_count += 1
           time.sleep(retry_delay)
           retry_delay *= 2  # Exponential backoff
   ```

2. **Session Recreation**: Recreates HTTP sessions when network changes
   ```python
   def reconnect_all_sessions(self):
       """Reset all network sessions when a network change is detected"""
       for account in self.accounts:
           if hasattr(account.session, 'close'):
               account.session.close()
           account.session = requests.Session()
   ```

3. **Network Watchdog**: Detects stale connections
   ```python
   # Watchdog timer for network issues
   last_successful_operation = time.time()
   network_watchdog_timeout = 60  # seconds
   
   if time.time() - last_successful_operation > network_watchdog_timeout:
       logger.warning("Network watchdog triggered! Resetting connections.")
       # Reset connections for all accounts
   ```

## Discord API Interaction

The bot interacts with Discord's API through direct HTTP requests:

### Channel Messages Endpoint
```
GET https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}
```

### Send Message Endpoint
```
POST https://discord.com/api/v9/channels/{channel_id}/messages
```
Request body:
```json
{
    "content": "message content",
    "tts": false
}
```

### Typing Indicator Endpoint
```
POST https://discord.com/api/v9/channels/{channel_id}/typing
```

## Configuration System

The bot uses a JSON configuration file to store state:

```json
{
  "channel_id": "YOUR_CHANNEL_ID_HERE",
  "current_count": 2364,
  "last_counter_index": 1,
  "counting_active": true,
  "run_hours": [1, 5],
  "min_delay": 1.0,
  "max_delay": 2.0,
  "count_limit": 1000000,
  "bot_usernames": ["counting", "Counting", "CountingBot", "APP", "APP counting"],
  "scan_interval": 30,
  "speed_mode": true,
  "messages_per_second": 3.361399999999999,
  "verify_last_message": false,
  "accounts": [
    {
      "username": "example_account1",
      "token": "TOKEN_HERE",
      "user_agent": "USER_AGENT_HERE",
      "message_count": 1789
    },
    {
      "username": "example_account2",
      "token": "TOKEN_HERE",
      "user_agent": "USER_AGENT_HERE",
      "message_count": 1785
    }
  ]
}
```

The configuration is loaded at startup and saved:
- After each count
- When settings are changed
- When a reset is detected
- Before terminating counting

## Threading Model

The bot uses threading to handle background tasks:

```python
def start_counting(self, force_reset=False):
    """Start the counting loop in a background thread"""
    if self.counting_active:
        logger.warning("Counting is already active")
        return False
        
    self.counting_active = True
    self.force_reset = force_reset
    
    # Start counting in a background thread
    self.counter_thread = Thread(target=self._counting_loop)
    self.counter_thread.daemon = True
    self.counter_thread.start()
    
    logger.info("Started counting")
    return True
```

This allows the bot to:
1. Continue counting in the background
2. Handle user input in the foreground
3. Keep the main thread responsive
4. Gracefully shutdown when needed 