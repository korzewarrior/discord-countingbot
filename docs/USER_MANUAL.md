# Discord Auto Counter - User Manual

## Getting Started

### Starting the Bot

To start the bot, run:

```bash
python auto_counter.py
```

This will display the main menu:

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

### Command Line Arguments

The bot supports several command line arguments for quick startup:

| Argument | Description |
|----------|-------------|
| `--start` | Start counting immediately |
| `--force` | Skip initial scan and use current count |
| `--fix` | Run emergency count mismatch fix |
| `--version` | Show bot version and exit |
| `--auto-restart` | Enable auto-restart after resets |
| `--smart-speed` | Enable smart speed adjustment |
| `--reconnect` | Reconnect all network sessions |

Example: `python auto_counter.py --auto-restart --smart-speed --force --start`

## Menu Options Explained

### Account Management

#### 1. Add Account
Add a new Discord account to the bot. You'll need:
- Discord username
- Discord token
- User agent (optional)

#### 2. Remove Account
Remove an account from the bot by username.

#### 3. List Accounts
Display all configured accounts.

### Channel Configuration

#### 4. Set Channel
Set the Discord channel ID where counting will occur.

#### 5. Configure Settings
Additional settings submenu:
- Set Min Delay: Minimum time between counts
- Set Max Delay: Maximum time between counts
- Set Run Hours: Hours during which counting should occur
- Add Bot Username: Add a bot username to detect resets
- Set Scan Interval: How often to scan for resets

### Count Control

#### 6. Set Count Limit (Test Mode)
Set a maximum number of counts to perform. Useful for testing.

#### 7. Scan Channel Now
Perform an immediate scan of the channel to determine the current count and check for resets.

#### 8. Start Counting
Begin automated counting in the configured channel.

#### 9. Stop Counting
Stop the automated counting process.

### Status and Information

#### 10. Show Status
Display the current status, including:
- Current count
- Counting status (active/inactive)
- Number of accounts
- Current configuration

### Speed Control

#### 11. Toggle Speed Mode
Enable or disable speed mode, which increases counting rate.

#### 12. Configure Speed
Set the messages per second rate for speed mode.

#### 13. Toggle Message Verification
Enable or disable verification of sent messages.

#### 14. LUDICROUS SPEED
Enable maximum speed mode (50 messages per second).

#### 15. SMART SPEED (Auto-Adjust)
Enable dynamic speed adjustment based on rate limits.

### Advanced Operations

#### 16. Force Start (Skip Initial Scan)
Start counting without scanning the channel first.

#### 17. EMERGENCY: Fix Count Mismatch
Emergency function to resolve count mismatches by scanning current messages.

#### 18. Toggle Auto-Restart After Reset
Enable or disable automatic restart after a count reset is detected.

#### 19. NETWORK: Reconnect All Sessions
Force reconnection of all network sessions. Useful after network changes.

## Operation Modes

### Normal Mode
- Regular counting with verification
- Moderate speed
- Manual restart after resets
- Suitable for most situations

### Speed Mode
- Faster counting
- Reduced verification
- May hit rate limits occasionally
- Good balance of speed and reliability

### Ludicrous Mode
- Maximum speed
- No verification
- High chance of rate limits
- Rapid counting until limited by Discord

### Smart Speed Mode
- Starts at medium speed
- Automatically adjusts based on rate limits
- Slows down when hitting limits
- Speeds up during smooth operation
- Best option for long-term operation

## Auto-Restart Mode

When enabled, auto-restart will:
1. Detect count resets from Discord bots
2. Automatically reset the counter to 0
3. Wait 3 seconds for Discord to stabilize
4. Restart counting from 1
5. Continue operation without manual intervention

Enable with: `--auto-restart` or menu option 18

## Network Management

### Automatic Network Recovery
The bot will automatically:
- Detect network disconnections
- Attempt to reconnect with exponential backoff
- Reset sessions after prolonged issues
- Continue counting once connection is restored

### Manual Network Recovery
If experiencing network issues:
1. Use option 19 to force reconnection
2. Check your internet connection
3. Restart the bot if needed

## Monitoring Bot Operation

### Console Output
The bot provides detailed logging in the console:

```
2025-03-04 18:24:22,285 - AutoCounter - INFO - Message sent by example_account1: 1771
2025-03-04 18:24:22,285 - AutoCounter - INFO - Configuration saved
2025-03-04 18:24:22,285 - AutoCounter - INFO - Count: 1771 | By: example_account1 | Progress: 1760/1000000
2025-03-04 18:24:22,285 - AutoCounter - INFO - Next count in 0.29 seconds
```

### Log Interpretation

| Log Level | Meaning |
|-----------|---------|
| INFO | Normal operation information |
| WARNING | Potential issues or significant events |
| ERROR | Problems requiring attention |

### Key Log Patterns

- **Reset Detection**: `WARNING - Reset detected with pattern: next number is \*\*1\*\*`
- **Count Progress**: `INFO - Count: 765 | By: example_account1 | Progress: 765/1000000`
- **Rate Limiting**: `WARNING - Rate limited! Waiting 0.5 seconds`
- **Network Issues**: `ERROR - Connection error when sending message`

## Best Practices

### Optimal Configuration
- Use at least 2 Discord accounts
- Enable auto-restart mode
- Use smart speed mode
- Set appropriate delays for your channel

### Performance Tuning
- Adjust message rate based on Discord activity
- Lower message rate during high traffic periods
- Increase scan interval if not needed frequently
- Use force start to avoid reading old messages

### Maintenance
- Periodically check for rate limiting patterns
- Monitor token validity
- Restart the bot if performance degrades
- Update user agents if needed

### Recovery Procedures
1. If counting stops: Use option 7 to scan and option 8 to restart
2. If count is wrong: Use option 17 to fix mismatches
3. If network changes: Use option 19 to reconnect sessions
4. If all else fails: Restart the bot with `--fix` followed by `--force --start`

## Advanced Usage Scenarios

### 24/7 Operation
For continuous operation:
1. Set run hours to cover the full day [0, 23]
2. Enable auto-restart
3. Enable smart speed
4. Use a reliable internet connection
5. Consider running as a service

### Collaborative Counting
To coordinate with other bots:
1. Add their bot usernames to the configuration
2. Adjust scan frequency to detect their messages
3. Configure appropriate delays

### Rate Limit Avoidance
To minimize Discord rate limiting:
1. Use multiple accounts
2. Enable smart speed mode
3. Avoid ludicrous mode for extended periods
4. Set reasonable message rates (5-15/second) 