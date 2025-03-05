# Discord Auto Counter Bot

A specialized bot designed to automate counting in Discord channels.

## Overview
The Discord Auto Counter is a sophisticated bot designed to automate counting in Discord channels. It handles user tokens, manages multiple accounts, detects count resets, and automatically continues counting. With features like auto-restart, network resilience, and smart speed control, it's designed to maintain counts even through disruptions.

## Key Features
- **Multi-Account Support**: Alternate between different accounts to avoid Discord's rate limits
- **Automatic Reset Detection**: Recognizes when the count is reset and restarts from 1
- **Network Resilience**: Automatically handles network changes and reconnects
- **Smart Speed Adjustment**: Dynamically adjusts counting speed based on Discord's rate limits
- **Emergency Recovery**: Tools to fix count mismatches and restore functionality

## Quick Start
1. Install the requirements: `pip install -r requirements.txt`
2. Run the setup script: `python setup.py` to create your configuration
3. Or configure manually: Copy `counter_config.template.json` to `counter_config.json` and edit
4. Run the bot: `python auto_counter.py --auto-restart --smart-speed --force --start`

## Usage Examples

### Basic Operation
```bash
# Start the bot with interactive menu
python auto_counter.py

# Start counting immediately with default settings
python auto_counter.py --start

# Start with optimized settings for long-term operation
python auto_counter.py --auto-restart --smart-speed --force --start
```

### Advanced Examples
```bash
# Scan channel without starting counting
python auto_counter.py --scan

# Fix count mismatch after a glitch
python auto_counter.py --fix

# Show current version
python auto_counter.py --version

# Reconnect all sessions after network change
python auto_counter.py --reconnect
```

### Example Bot Menu
```
=== Discord Auto Counter ===
1. Add Account
2. Remove Account
3. List Accounts
4. Set Channel
5. Configure Settings
6. Set Count Limit (Test Mode)
7. Scan Channel Now
8. Start Counting
9. Stop Counting
10. Show Status
11. Toggle Speed Mode
12. Configure Speed
13. Toggle Message Verification
14. LUDICROUS SPEED
15. SMART SPEED (Auto-Adjust)
16. Force Start (Skip Initial Scan)
17. EMERGENCY: Fix Count Mismatch
18. Toggle Auto-Restart After Reset
19. NETWORK: Reconnect All Sessions
0. Exit
```

## Screenshots

<!-- 
Screenshots would typically be added here. For example:

![Bot in Action](screenshots/bot_counting.png)
![Configuration Menu](screenshots/configuration_menu.png)
![Status Display](screenshots/status_display.png)
-->

*Note: Add screenshots to a `screenshots/` directory and update the image links above.*

## Main Components
- Account management system
- Channel scanning and count detection
- Reset detection and auto-restart
- Network resilience mechanisms
- Rate limiting adaptation

## Documentation
For complete documentation, please refer to the documents in the `docs/` folder:

- [Setup Guide](docs/SETUP_GUIDE.md)
- [User Manual](docs/USER_MANUAL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Technical Details](docs/TECHNICAL_DETAILS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Performance Optimization](docs/PERFORMANCE.md)
- [Security Considerations](docs/SECURITY.md)
- [Extending the Bot](docs/EXTENDING.md)
- [Frequently Asked Questions](docs/FAQ.md)
- [Coding Standards](docs/CODING_STANDARDS.md)

For a complete overview of the documentation, see the [Documentation README](docs/README.md).

## Project Structure

```
discord-countingbot/
├── auto_counter.py              # Main bot implementation
├── setup.py                     # Configuration setup helper
├── counter_config.template.json # Template configuration file
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License with disclaimer
├── README.md                    # This file
└── docs/                        # Documentation
    ├── README.md                # Documentation overview
    ├── SETUP_GUIDE.md
    └── ...
```

## Security Notice

**IMPORTANT**: Never commit your actual Discord tokens or other sensitive information to a public repository. The included `.gitignore` file is configured to prevent accidental commits of your `counter_config.json` file.

## Disclaimer

This software is provided for educational purposes only. Use of this bot may violate Discord's Terms of Service, particularly regarding automation of user accounts. The author does not take responsibility for any consequences resulting from the use of this software.

## License

This project is available under the MIT License with an additional disclaimer. See the [LICENSE](LICENSE) file for details. 