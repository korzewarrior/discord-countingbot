# Discord Auto Counter - Troubleshooting Guide

## Common Issues and Solutions

### Bot Not Starting

#### Symptoms
- Error when starting the bot
- Python errors in console
- Bot immediately exits

#### Possible Causes and Solutions

1. **Missing Dependencies**
   - **Error**: `ModuleNotFoundError: No module named 'requests'`
   - **Solution**: Install required packages: `pip install -r requirements.txt`

2. **Invalid Python Version**
   - **Error**: Syntax errors or unexpected keyword arguments
   - **Solution**: Ensure you're using Python 3.6+ with `python --version`

3. **Permission Issues**
   - **Error**: `Permission denied` when accessing configuration
   - **Solution**: Check file permissions on `counter_config.json`

4. **Invalid JSON Configuration**
   - **Error**: `json.decoder.JSONDecodeError`
   - **Solution**: Validate JSON format in `counter_config.json`

### Bot Not Counting

#### Symptoms
- Bot starts but doesn't send messages
- "Started counting" appears but no counts in Discord
- Errors about sending messages

#### Possible Causes and Solutions

1. **Invalid Token**
   - **Error**: `401 Unauthorized` in logs
   - **Solution**: Update token in configuration or add new account

2. **Invalid Channel ID**
   - **Error**: `404 Not Found` in logs
   - **Solution**: Verify and correct channel ID in configuration

3. **Insufficient Permissions**
   - **Error**: `403 Forbidden` in logs
   - **Solution**: Ensure account has permission to post in channel

4. **Rate Limiting**
   - **Error**: `429 Too Many Requests` in logs
   - **Solution**: 
     - Reduce message rate with option 12
     - Add more accounts
     - Use smart speed mode (option 15)

5. **Network Issues**
   - **Error**: `Connection error` or timeout messages
   - **Solution**: 
     - Check internet connection
     - Use option 19 to reconnect sessions
     - Restart bot

### Incorrect Counting

#### Symptoms
- Bot skips numbers
- Bot repeats numbers
- Bot continues after reset with wrong numbers

#### Possible Causes and Solutions

1. **Scanning Issues**
   - **Error**: `Scan results: Current count = [unexpected number]`
   - **Solution**: Use option 17 to fix count mismatch

2. **Reset Detection Failure**
   - **Error**: Bot misses reset messages
   - **Solution**: 
     - Add bot username to configuration if missing
     - Check reset patterns in code
     - Use option 7 to force scan

3. **Duplicate Counts**
   - **Error**: Multiple bots counting the same number
   - **Solution**: 
     - Ensure only one bot instance is running
     - Verify no other bots are counting

4. **Last Counter Tracking Issue**
   - **Error**: Bot uses same account repeatedly
   - **Solution**: Reset configuration or set `last_counter_index` to `null`

### Network-Related Issues

#### Symptoms
- Connection timeouts
- Bot freezes after network changes
- "Error sending message" logs

#### Possible Causes and Solutions

1. **WiFi/Network Changes**
   - **Error**: `Connection error when sending message` after network change
   - **Solution**: 
     - Use option 19 to reconnect all sessions
     - Wait for automatic network watchdog to trigger
     - Restart bot with `--reconnect` flag

2. **Connection Timeouts**
   - **Error**: `Read timed out` in logs
   - **Solution**: 
     - Check internet stability
     - Reduce message rate
     - Use automatic retry mechanism

3. **DNS Issues**
   - **Error**: `Failed to resolve hostname` or similar
   - **Solution**: 
     - Check DNS settings
     - Try using static IPs in hosts file
     - Restart network equipment

### Rate Limiting Issues

#### Symptoms
- "Rate limited" messages in logs
- Bot slowing down dramatically
- "Too many rate limits" warnings

#### Possible Causes and Solutions

1. **Excessive Speed**
   - **Error**: Frequent rate limit messages
   - **Solution**: 
     - Reduce `messages_per_second` in configuration
     - Use smart speed instead of ludicrous mode
     - Add more accounts to distribute load

2. **Discord Temporary Blocks**
   - **Error**: Persistent rate limits despite lowering speed
   - **Solution**: 
     - Stop counting for several hours
     - Rotate to different accounts
     - Check if account is flagged by Discord

3. **IP-Based Rate Limiting**
   - **Error**: All accounts getting rate limited together
   - **Solution**: 
     - Use accounts on different IPs
     - Consider using a proxy (advanced)
     - Reduce overall activity

### Bot Crashes or Exits Unexpectedly

#### Symptoms
- Bot terminates without warning
- Python exceptions in console
- Process no longer running

#### Possible Causes and Solutions

1. **Unhandled Exceptions**
   - **Error**: Python tracebacks ending with exceptions
   - **Solution**: 
     - Check the specific exception
     - Implement error handling for that case
     - Run bot with error output redirected to file

2. **Memory Issues**
   - **Error**: `MemoryError` or system becoming unresponsive
   - **Solution**: 
     - Check for memory leaks
     - Restart bot periodically
     - Limit message history stored in memory

3. **External Termination**
   - **Error**: Process killed by system
   - **Solution**: 
     - Run as service with restart capability
     - Check system logs for OOM killer
     - Ensure sufficient resources

## Diagnostic Procedures

### Checking Bot Status

To determine the current state of the bot:

1. Use option 10 from the menu to show status
2. Check the following information:
   - Current count
   - Counting active status
   - Number of accounts
   - Last counter used

### Scanning Channel Manually

To verify the current state of the Discord channel:

1. Use option 7 from the menu to scan the channel
2. Review the output for:
   - Current count detected
   - Last counter detected
   - Any reset messages detected

### Network Connectivity Test

To test network connectivity:

1. Use option 19 to reconnect all sessions
2. Check if reconnection was successful
3. Try sending a test count with option 8 (start counting)
4. Stop counting with option 9 if successful

### Rate Limit Diagnosis

To diagnose rate limiting issues:

1. Check logs for "Rate limited" messages
2. Note frequency and duration of rate limits
3. Check if specific accounts are rate limited more often
4. Try reducing message rate with option 12

### Reset Detection Test

To test reset detection:

1. Manually trigger a reset in Discord
2. Watch logs for reset detection messages
3. Verify auto-restart behavior if enabled
4. Check if count resets to 0 and next count is 1

## Advanced Troubleshooting

### Debugging Mode

To run the bot with detailed logging:

```bash
python -u auto_counter.py > bot_debug.log 2>&1
```

This will capture all output to a log file for analysis.

### Inspecting Configuration

To inspect the current configuration:

```bash
cat counter_config.json | python -m json.tool
```

This will format the JSON file for easier reading.

### Resetting to Default State

If the bot is in an unrecoverable state:

1. Stop the bot
2. Backup the current configuration: `cp counter_config.json counter_config.backup.json`
3. Reset the configuration:

```json
{
  "channel_id": "YOUR_CHANNEL_ID",
  "current_count": 0,
  "last_counter_index": null,
  "counting_active": false,
  "run_hours": [0, 23],
  "min_delay": 1.0,
  "max_delay": 3.0,
  "count_limit": null,
  "bot_usernames": ["counting", "Counting", "CountingBot", "APP", "APP counting"],
  "scan_interval": 30,
  "speed_mode": false,
  "messages_per_second": 5.0,
  "verify_last_message": true,
  "accounts": [
    // Keep your existing accounts here
  ]
}
```

4. Restart the bot with `--fix` followed by `--force --start`

### Monitoring Network Activity

To monitor the bot's network activity:

```bash
sudo tcpdump -i any -n host discord.com -w discord_traffic.pcap
```

This captures all traffic to/from Discord for analysis.

### Testing Discord API Access

To test Discord API access directly:

```bash
curl -s -H "Authorization: YOUR_TOKEN" https://discord.com/api/v9/users/@me | python -m json.tool
```

If successful, you should see your account information.

## Problem Escalation Procedure

If unable to resolve an issue:

1. Collect detailed logs with timestamps
2. Note the exact symptoms and behavior
3. Document the steps already taken
4. Check Discord service status
5. Consider API changes that might affect the bot
6. Create detailed report with all information 