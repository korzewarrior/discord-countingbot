# Discord Auto Counter - Setup and Installation Guide

## Prerequisites

Before installing the Discord Auto Counter, ensure you have:

1. **Python 3.6 or higher** installed
2. **pip** (Python package manager) installed
3. Discord accounts with valid tokens
4. Basic knowledge of Discord channel IDs

## Installation Steps

### Step 1: Clone or Download the Project

Download the project files to your local machine.

### Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `requests`: For API communication
- `schedule`: For scheduling tasks
- `python-dateutil`: For date/time handling

### Step 3: Configure the Bot

1. Create a new file named `counter_config.json` (if it doesn't exist)
2. Add the following structure:

```json
{
  "channel_id": "",
  "current_count": 0,
  "last_counter_index": null,
  "counting_active": false,
  "run_hours": [0, 23],
  "min_delay": 1.0,
  "max_delay": 3.0,
  "count_limit": null,
  "bot_usernames": [
    "counting",
    "Counting",
    "CountingBot",
    "APP",
    "APP counting"
  ],
  "scan_interval": 30,
  "speed_mode": false,
  "messages_per_second": 5.0,
  "verify_last_message": true,
  "accounts": []
}
```

### Step 4: Add Discord Accounts

#### Method 1: Using the Bot Interface

1. Start the bot: `python auto_counter.py`
2. Choose option 1 from the menu
3. Enter your Discord username
4. Enter your account token
5. Enter your user agent (optional, press Enter to use default)

#### Method 2: Directly Edit Configuration

Add accounts directly to the `counter_config.json` file:

```json
"accounts": [
  {
    "username": "your_discord_username",
    "token": "your_discord_token",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "message_count": 0
  }
]
```

### Step 5: Set the Discord Channel

#### Method 1: Using the Bot Interface

1. Start the bot: `python auto_counter.py`
2. Choose option 4 from the menu
3. Enter the Discord channel ID

#### Method 2: Directly Edit Configuration

Set the `channel_id` in `counter_config.json`:

```json
"channel_id": "1234567890123456789"
```

## Obtaining Discord Tokens

> **IMPORTANT**: Using user tokens for automation may violate Discord's Terms of Service. This information is provided for educational purposes only.

To obtain a Discord token:

1. Open Discord in your web browser
2. Press F12 to open Developer Tools
3. Go to the "Network" tab
4. Type something in any Discord channel
5. Look for a request to the "messages" endpoint
6. Find the "authorization" header in the request
7. The value of this header is your token

## Finding Channel IDs

To find a Discord channel ID:

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the channel you want to use
3. Select "Copy ID"

## Configuration Options Explained

| Option | Description |
|--------|-------------|
| `channel_id` | Discord channel ID where counting will occur |
| `current_count` | The current count (set to 0 to start fresh) |
| `last_counter_index` | Index of the last account that counted |
| `counting_active` | Whether counting is currently active |
| `run_hours` | Hours during which counting should occur [start, end] |
| `min_delay` | Minimum delay between counts (seconds) |
| `max_delay` | Maximum delay between counts (seconds) |
| `count_limit` | Maximum number of counts to perform (null for unlimited) |
| `bot_usernames` | List of bot usernames to detect reset messages |
| `scan_interval` | How often to scan for resets (seconds) |
| `speed_mode` | Enable faster counting with less verification |
| `messages_per_second` | Message rate when in speed mode |
| `verify_last_message` | Whether to verify messages after sending |
| `accounts` | List of Discord accounts to use for counting |

## Advanced Setup Options

### Run as a Background Service

You can set up the bot to run as a background service using tools like:
- **Linux**: systemd
- **Windows**: Task Scheduler
- **macOS**: launchd

Example systemd service file (`discord-counter.service`):

```
[Unit]
Description=Discord Auto Counter Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/auto_counter.py --auto-restart --smart-speed --force --start
WorkingDirectory=/path/to/bot/directory
StandardOutput=append:/var/log/discord-counter.log
StandardError=append:/var/log/discord-counter.error.log
Restart=always
User=yourusername

[Install]
WantedBy=multi-user.target
```

### Multiple Instances Setup

To run multiple instances for different channels:

1. Create separate configuration files for each channel
2. Run each instance with a different configuration file:

```bash
python auto_counter.py --config channel1_config.json --auto-restart --start &
python auto_counter.py --config channel2_config.json --auto-restart --start &
```

## Recommended Setup for Best Performance

For optimal performance and reliability:

1. Use at least 2 Discord accounts
2. Enable auto-restart mode
3. Enable smart speed mode
4. Use appropriate run hours (if counting should be limited)

Recommended command line:

```bash
python auto_counter.py --auto-restart --smart-speed --force --start
```

This configuration will:
- Start counting immediately
- Skip initial scan to avoid reading old messages
- Automatically restart after resets
- Dynamically adjust speed based on rate limits

## Verifying Successful Installation

To verify the bot is working properly:

1. Start the bot with counting enabled
2. Monitor the console output for logging information
3. Check the Discord channel to see if counts are being posted
4. Monitor for any error messages

If errors occur, refer to the [Troubleshooting Guide](TROUBLESHOOTING.md). 