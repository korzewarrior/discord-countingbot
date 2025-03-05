# Discord Auto Counter - Performance Optimization Guide

## Understanding Discord Rate Limits

Discord applies rate limits to control API usage:

- **Global Rate Limits**: Apply across all endpoints
- **Resource-Specific Rate Limits**: Apply to specific endpoints
- **User-Based Rate Limits**: Apply to specific users/tokens

The bot primarily interacts with two rate-limited endpoints:
1. **Send Message** (`POST /channels/{channel_id}/messages`)
2. **Get Channel Messages** (`GET /channels/{channel_id}/messages`)

## Speed Modes Explained

### Standard Mode
- Default operation mode
- ~1 message per 1-3 seconds
- Full verification of sent messages
- Minimal rate limiting
- Safest option for long-term operation

### Speed Mode
- Faster counting without verification
- 5-10 messages per second
- Occasional rate limiting
- Good balance of speed and reliability
- Enable with option 11 or `toggle_speed_mode()`

### Ludicrous Mode
- Maximum speed counting
- 20+ messages per second
- Frequent rate limiting
- Limited verification and safety checks
- For short bursts of rapid counting
- Enable with option 14 or message rate >20

### Smart Speed Mode
- Adaptive speed based on rate limits
- Starts at 20 messages per second
- Automatically adjusts as needed
- Increases speed after successful periods
- Decreases speed after rate limits
- Best option for optimized performance
- Enable with option 15 or `smart_speed()`

## Rate Limit Handling

The bot manages rate limits through several mechanisms:

### Detection
```python
if response.status_code == 429:
    # Handle rate limiting
    try:
        data = response.json()
        retry_after = data.get('retry_after', 1)
        logger.warning(f"RATE LIMITED: Must wait {retry_after} seconds before next message")
        return False, {"rate_limited": True, "retry_after": retry_after}
    except:
        logger.warning("Rate limited but couldn't parse response")
        return False, {"rate_limited": True, "retry_after": 1}
```

### Adaptive Delay
```python
# Increase delay modifier after rate limit hit
if current_delay_modifier < MAX_DELAY_MODIFIER:
    current_delay_modifier = min(MAX_DELAY_MODIFIER, current_delay_modifier * 1.5)
    
# Log warning
logger.warning(f"Rate limited! Waiting {retry_after} seconds")

# Wait before trying again
time.sleep(retry_after)
```

### Dynamic Speed Adjustment
```python
# After successful message
successful_messages += 1

# Speed up if consistently successful
if successful_messages >= SUCCESSFUL_THRESHOLD:
    successful_messages = 0
    if messages_per_second < MAX_MESSAGES_PER_SECOND:
        messages_per_second *= 1.1
        logger.info(f"Speed increased to {messages_per_second:.2f} messages/second")
```

## Multi-Account Strategy

The bot alternates between accounts to distribute rate limits:

### Advantages
1. **Higher Throughput**: Each account has its own rate limit bucket
2. **Resilience**: If one account gets heavily rate-limited, others continue
3. **Natural Counting Flow**: Simulates multiple users counting together

### Implementation
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

### Optimal Account Usage
- **Minimum**: 2 accounts (alternating)
- **Recommended**: 3-5 accounts (optimal distribution)
- **Maximum**: Limited by your coordination capacity

## Network Performance Tuning

### Persistent Sessions
The bot maintains persistent HTTP sessions for efficiency:

```python
def __init__(self, username, user_token, user_agent=None):
    self.username = username
    self.token = user_token
    self.user_agent = user_agent or DEFAULT_USER_AGENT
    self.session = requests.Session()
    self.setup_session()
    
def setup_session(self):
    """Configure session headers and settings"""
    self.session.headers.update({
        "Authorization": self.token,
        "User-Agent": self.user_agent,
        "Content-Type": "application/json"
    })
```

### Connection Pooling
Using persistent sessions provides connection pooling benefits:
- Reuses TCP connections
- Reduces SSL handshake overhead
- Utilizes HTTP Keep-Alive
- Maintains cookies between requests

### Network Timeout Settings
Customizable timeout settings prevent hanging on slow networks:

```python
# Default timeout values
DEFAULT_TIMEOUT = 10.0  # seconds
LONG_TIMEOUT = 30.0     # seconds for initial connections

# Apply timeout to request
try:
    response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
except requests.exceptions.Timeout:
    logger.error(f"Request timed out: {url}")
    return False, {"error": "timeout"}
```

## Memory Optimization

### Efficient Message Processing
The bot processes messages efficiently to minimize memory usage:

```python
# Extract only needed fields from message
messages = response.json()
simplified_messages = []

for msg in messages:
    if not all(key in msg for key in ["id", "content", "author", "timestamp"]):
        continue
    
    # Extract only needed fields
    simplified_messages.append({
        "id": msg["id"],
        "content": msg["content"],
        "author": {
            "id": msg["author"]["id"],
            "username": msg["author"]["username"]
        },
        "timestamp": msg["timestamp"]
    })

return simplified_messages
```

### Message Limit Control
Controls the number of messages retrieved to balance accuracy with performance:

```python
def get_channel_messages(self, channel_id, limit=30):
    """Get messages from a Discord channel
    
    Args:
        channel_id (str): The channel ID to get messages from
        limit (int): Number of messages to retrieve (max 100)
    """
    if limit > 100:
        limit = 100  # Discord API limit
        
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
    # Fetch and process messages
```

## Scan Optimization

### Selective Scanning
The bot implements selective scanning to minimize API calls:

```python
# Only scan every N loop iterations
if loop_count % scan_interval != 0:
    # Skip scan this time
    logger.debug("Skipping scan this loop iteration")
    continue
    
# Perform full scan
scan_result = self.scan_channel()
```

### Time-Based Filtering
Filters messages based on time to avoid processing old messages:

```python
# Only consider recent messages for reset detection
recent_timestamp = datetime.now() - timedelta(minutes=5)
logger.info(f"Only considering reset messages newer than: {recent_timestamp}")

# Filter messages
for message in messages:
    message_timestamp = parse_discord_timestamp(message["timestamp"])
    if message_timestamp < recent_timestamp:
        # Skip old messages
        continue
```

## Threading Model Optimization

### Background Processing
The bot uses a background thread for counting to keep the UI responsive:

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

### Thread Safety
Ensures thread safety for configuration access and modification:

```python
def save_config(self):
    """Save configuration to file (thread-safe)"""
    with self.config_lock:
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    logger.info("Configuration saved")
```

## Configuration Optimization

### Recommended Settings

#### For Reliability (24/7 Operation)
```json
{
  "messages_per_second": 5.0,
  "verify_last_message": true,
  "speed_mode": false,
  "scan_interval": 30,
  "min_delay": 1.0,
  "max_delay": 3.0
}
```

#### For Speed (Short-Term Max Counting)
```json
{
  "messages_per_second": 20.0,
  "verify_last_message": false,
  "speed_mode": true,
  "scan_interval": 60,
  "min_delay": 0.05,
  "max_delay": 0.5
}
```

#### For Balanced Operation (Recommended)
```json
{
  "messages_per_second": 10.0,
  "verify_last_message": false,
  "speed_mode": true,
  "scan_interval": 30,
  "min_delay": 0.3,
  "max_delay": 1.0
}
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Message Success Rate**:
   - Track successful vs. failed message sends
   - Target: >95% success rate

2. **Rate Limit Frequency**:
   - Count rate limit responses (429)
   - Target: <5% of requests

3. **Message Rate**:
   - Messages sent per minute
   - Target: As high as possible without excessive rate limits

4. **Scan Efficiency**:
   - Time taken to scan channel
   - Target: <1 second per scan

### Sample Log Analysis
Track these patterns in logs:

```
Rate limited: 15 times in last hour (3.5%)
Message success: 412/425 messages (96.9%)
Average message rate: 6.9 messages/minute
Average scan time: 0.32 seconds
```

## Advanced Performance Techniques

### User Agent Rotation
Simulate different clients to potentially distribute rate limits:

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

def rotate_user_agent(self):
    """Rotate to a different user agent"""
    new_agent = random.choice(USER_AGENTS)
    self.session.headers.update({"User-Agent": new_agent})
    logger.info(f"Rotated user agent: {new_agent[:30]}...")
```

### Message Queue Management
Implement a message queue to manage sending:

```python
# Message queue with rate limiting
message_queue = []
last_send_time = 0
min_send_interval = 1.0 / messages_per_second

def enqueue_message(self, channel_id, content, account_index):
    """Add message to send queue"""
    message_queue.append({
        "channel_id": channel_id,
        "content": content,
        "account": account_index,
        "added_time": time.time()
    })
    
def process_queue(self):
    """Process message queue with rate limiting"""
    while message_queue and (time.time() - last_send_time) >= min_send_interval:
        msg = message_queue.pop(0)
        success = self.accounts[msg["account"]].send_message(
            msg["channel_id"], msg["content"]
        )
        last_send_time = time.time()
        
        if not success and time.time() - msg["added_time"] < 60:
            # Re-queue if recent and failed
            message_queue.append(msg)
```

### Adaptive Scan Interval
Dynamically adjust scan frequency based on channel activity:

```python
def adaptive_scan_interval(self, message_rate):
    """Adjust scan interval based on message rate
    
    Higher message rates -> less frequent scans
    Lower message rates -> more frequent scans
    """
    base_interval = 30  # baseline scan interval in seconds
    
    if message_rate > 10:
        # Very active channel, scan less frequently
        return min(120, base_interval * (message_rate / 5))
    elif message_rate < 2:
        # Quiet channel, scan more frequently
        return max(10, base_interval / 2)
    else:
        # Normal activity, use base interval
        return base_interval
```

## Performance Benchmarks

### Target Performance Metrics

| Metric | Basic | Good | Excellent |
|--------|-------|------|-----------|
| Messages per minute | <30 | 30-120 | >120 |
| Scan time (seconds) | >3 | 1-3 | <1 |
| Rate limit frequency | >10% | 2-10% | <2% |
| Memory usage (MB) | >100 | 50-100 | <50 |
| CPU usage (%) | >10 | 5-10 | <5 |

### Achieving Maximum Performance

To achieve maximum counting performance:

1. Use at least 3 different accounts
2. Enable smart speed mode
3. Set scan interval to 60 seconds
4. Disable message verification
5. Run during off-peak Discord hours
6. Use a reliable, low-latency network connection
7. Run on dedicated hardware with stable internet 