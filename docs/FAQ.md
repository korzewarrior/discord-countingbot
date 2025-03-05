# Discord Auto Counter - Frequently Asked Questions

## General Questions

### Q: What is the Discord Auto Counter bot?
**A:** The Discord Auto Counter is a specialized tool that automates participation in Discord counting channels. It can detect the current count in a channel, continue the count sequence automatically, handle resets, and manage multiple user accounts for a more natural counting experience.

### Q: Is this bot against Discord's Terms of Service?
**A:** Yes. Discord's Terms of Service prohibit automation of user accounts ("self-bots"). This tool is provided for educational purposes only. Using this bot may result in account warnings or termination. Use at your own risk.

### Q: Can I get banned for using this?
**A:** Yes, there is a risk of account action from Discord. The bot includes various features to reduce detection risk, but there is always a possibility that automated activity could be detected and result in account actions.

### Q: How many accounts do I need to use this bot?
**A:** You can use the bot with a single account, but it works best with 2-5 accounts. Using multiple accounts allows for more natural counting patterns and distributes rate limits across different accounts.

### Q: How fast can the bot count?
**A:** The bot supports several speed modes:
- Standard mode: ~1 count every 1-3 seconds (safest)
- Speed mode: ~5-10 counts per second
- Ludicrous mode: ~20+ counts per second (high risk of rate limiting)
- Smart speed mode: Adjusts dynamically based on rate limits

## Setup & Configuration

### Q: How do I get my Discord token?
**A:** For security reasons, we do not provide instructions on how to obtain Discord tokens. However, if you're using this for educational purposes, you can find information about Discord's API authentication in their developer documentation.

### Q: Where is the configuration stored?
**A:** The configuration is stored in `counter_config.json` in the same directory as the script. This file contains your settings, channel information, and the current count.

### Q: Can I run the bot on multiple channels?
**A:** Yes, you can run multiple instances of the bot with different configuration files. For example:
```
python auto_counter.py --config counter_config_channel1.json
python auto_counter.py --config counter_config_channel2.json
```

### Q: How do I set up the bot to work with a specific channel?
**A:** You need to configure the channel ID in the menu (option 3). You can get a channel ID by enabling Developer Mode in Discord (Settings > Advanced > Developer Mode), then right-clicking on the channel and selecting "Copy ID".

### Q: Can I use the bot without entering my token every time?
**A:** Yes, once you've added an account using option 1, the token is saved (in an encrypted form) in the configuration file. You don't need to re-enter it unless you delete the configuration file or change accounts.

## Operations & Usage

### Q: How do I start counting?
**A:** Use option 8 in the menu to start the counting process. The bot will scan the channel, determine the current count, and begin counting from the next number.

### Q: How do I stop the bot?
**A:** You can use option 9 to stop counting operations, or press Ctrl+C to exit the program entirely.

### Q: How does the bot detect the current count?
**A:** The bot scans the most recent messages in the channel and looks for the last valid number. It then increments from that number.

### Q: What happens if someone else counts while the bot is running?
**A:** The bot periodically scans the channel to detect if someone else has counted. If it detects that the count has changed, it will adjust its next count accordingly.

### Q: How does the bot handle resets?
**A:** The bot can detect reset messages (often sent by counting bots when someone makes a mistake). When it detects a reset, it can either:
1. Stop counting and require manual restart (default)
2. Automatically restart from 1 if auto-restart is enabled

### Q: Can the bot count in patterns other than 1, 2, 3...?
**A:** Yes, the bot can be extended to support different counting patterns like Fibonacci sequences, powers of 2, or other custom sequences. See the EXTENDING.md document for details.

### Q: How can I make the bot count faster?
**A:** You can enable speed mode (option 11) or smart speed (option 15). For maximum speed (but higher risk of detection), you can use ludicrous mode (option 14).

### Q: Does the bot support typing indicators?
**A:** Yes, by default the bot simulates typing before sending a number, making the counting appear more natural.

## Troubleshooting

### Q: The bot is not counting. What's wrong?
**A:** Check the following:
1. Verify you've set the correct channel ID
2. Ensure your token is valid
3. Check if you have permission to send messages in the channel
4. Look for error messages in the console
5. Make sure counting is started (option 8)

### Q: The bot keeps getting the count wrong. Why?
**A:** This could happen if:
1. Multiple people are counting at once
2. The channel has a counting pattern the bot doesn't understand
3. The bot is not scanning frequently enough to detect count changes

Try increasing the scan interval or check that the channel follows a standard counting pattern.

### Q: I'm getting rate limit errors. What does this mean?
**A:** Discord limits how many actions an account can perform in a given time period. Rate limit errors mean you're sending messages too quickly. Try:
1. Using a slower counting mode
2. Adding more accounts to distribute the counting
3. Enabling smart speed mode to automatically adjust

### Q: The bot stopped after detecting a reset. How do I restart it?
**A:** By default, the bot stops counting when it detects a reset. You can:
1. Use option 8 to start counting again (it will start from 1)
2. Enable auto-restart mode (option 16) to automatically continue after resets

### Q: The bot freezes when I change WiFi/networks. How do I fix this?
**A:** The latest version includes network resilience features. If the bot still freezes:
1. Use option 17 to manually reconnect all network sessions
2. Restart the bot with the `--reconnect` flag
3. Update to the latest version which includes better network handling

### Q: How can I see what the bot is doing?
**A:** The bot logs all its activities to the console. For more detailed logs, you can enable debug mode with the `--debug` flag when starting:
```
python auto_counter.py --debug
```

## Performance & Optimization

### Q: How many messages can the bot handle per minute?
**A:** This depends on several factors:
- Number of accounts used
- Discord's current rate limits
- Network conditions
- Selected speed mode

In optimal conditions with multiple accounts and speed mode enabled, the bot can handle hundreds of counts per minute.

### Q: Does the bot use a lot of system resources?
**A:** No, the bot is designed to be lightweight. It typically uses:
- <5% CPU
- ~50MB of RAM
- Minimal network bandwidth

### Q: Is there a way to reduce API usage?
**A:** Yes:
1. Increase the scan interval (less frequent channel checks)
2. Disable typing indicators
3. Disable message verification

### Q: How can I optimize for long-term operation?
**A:** For 24/7 operation:
1. Use standard mode (slower but more reliable)
2. Use multiple accounts (3-5 recommended)
3. Enable auto-restart
4. Run on a stable internet connection
5. Consider running in a Docker container for isolation

## Security & Safety

### Q: How secure is my token in the configuration file?
**A:** The bot attempts basic obfuscation of tokens, but for maximum security:
1. Never share your configuration file
2. Run the bot in a secure environment
3. Consider using environment variables instead of the config file
4. Regularly change your Discord password (which invalidates old tokens)

### Q: Can other people see that I'm using a bot?
**A:** The bot includes features to appear more human-like:
- Variable typing times
- Randomized delays between messages
- Natural message patterns

However, extremely fast counting or 24/7 operation may appear suspicious.

### Q: What should I do if I think my token was compromised?
**A:** Immediately:
1. Change your Discord password (which invalidates all tokens)
2. Enable two-factor authentication if you haven't already
3. Review your account for any unauthorized access
4. Generate a new token and update the bot's configuration

## Advanced Usage

### Q: Can I customize the bot's appearance or behavior?
**A:** Yes, see the EXTENDING.md document for details on:
- Custom counting patterns
- Message formatting
- Event hooks
- Plugin system

### Q: Can the bot be run headless (without a UI)?
**A:** Yes, you can run the bot in headless mode with command line arguments:
```
python auto_counter.py --start --force --auto-restart --no-ui
```

### Q: Can I use webhooks instead of user accounts?
**A:** No, the bot is specifically designed for counting channels that require user accounts. Webhooks cannot participate in counting channels.

### Q: Can the bot be scheduled to run at certain times?
**A:** The bot itself doesn't have scheduling capabilities, but you can use your operating system's scheduling tools (like cron on Linux or Task Scheduler on Windows) to start and stop the bot at specific times.

## Project & Development

### Q: Is this project still maintained?
**A:** As of the latest documentation update, yes. Check the repository for the most recent commits.

### Q: How can I contribute to the project?
**A:** See the EXTENDING.md document for guidelines on contributing. Generally:
1. Fork the repository
2. Make your changes
3. Submit a pull request with a clear description

### Q: Are there any plans for future features?
**A:** Potential future features include:
- Web interface for remote monitoring
- More sophisticated human-like behavior
- Additional counting games support
- Better statistics and analytics

### Q: Where can I report bugs or suggest features?
**A:** You can open issues on the project's repository or contact the maintainer directly.

### Q: Can I modify and redistribute this code?
**A:** Check the license in the repository for specific terms. Generally, this project is for educational purposes, and any redistributions should maintain appropriate attributions and disclaimers regarding Discord's Terms of Service. 