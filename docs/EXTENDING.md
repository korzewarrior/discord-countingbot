# Discord Auto Counter - Extending & Customizing

This document provides guidelines for developers who want to extend, customize, or integrate the Discord Auto Counter bot into other applications.

## Architecture Overview

Before modifying the code, understand the main architectural components:

1. **DiscordAccount**: Handles all Discord API interactions for individual accounts
2. **AutoCounter**: The core class managing the counting logic
3. **Main Menu**: The interface for user interaction
4. **Configuration System**: Handles persistence of settings

## Adding New Features

### Step 1: Plan Your Feature

Before coding, consider:
- Does it interact with Discord's API?
- Does it require UI changes?
- Will it impact performance?
- Will it require configuration changes?

### Step 2: Choose Where to Implement

For features that:
- **Interact with Discord API**: Add to `DiscordAccount` class
- **Modify counting behavior**: Add to `AutoCounter` class
- **Add user options**: Modify the menu system
- **Change data storage**: Update configuration handling

### Step 3: Implementation Pattern

Follow this pattern for implementing new features:

1. Add necessary properties to the appropriate class
2. Implement the core functionality as a dedicated method
3. Add configuration options if needed
4. Update documentation
5. Add any UI elements to control the feature

## Adding Custom Counting Modes

The bot supports several counting modes, and you can add more:

```python
def add_custom_counting_mode(self, mode_name, mode_function, description):
    """
    Add a custom counting mode
    
    Args:
        mode_name (str): Name of mode for configuration
        mode_function (callable): Function that returns the next count
        description (str): Description for UI
    """
    self.custom_modes[mode_name] = {
        "function": mode_function,
        "description": description
    }
    logger.info(f"Added custom counting mode: {mode_name}")
```

Example implementation:

```python
# Define custom counting function
def fibonacci_mode(current_count):
    """Fibonacci sequence counting mode"""
    # Initialize sequence if starting
    if current_count == 0:
        return 1
    if current_count == 1:
        return 1
        
    # Calculate next Fibonacci number
    # Get the last two numbers from channel history
    messages = self.scan_channel(limit=5)
    nums = []
    for msg in messages:
        if msg["content"].isdigit():
            nums.append(int(msg["content"]))
            if len(nums) >= 2:
                break
    
    if len(nums) >= 2:
        return nums[0] + nums[1]
    return 1  # Default if history not found
    
# Register the custom mode
counter.add_custom_counting_mode(
    "fibonacci", 
    fibonacci_mode,
    "Count in Fibonacci sequence (1,1,2,3,5,8,13...)"
)
```

## Modifying the User Interface

### Adding a Menu Option

To add a new menu option:

```python
def display_menu():
    # ... existing menu options ...
    
    print("16. [New Feature] My custom feature")
    
    # ... existing code ...
    
    elif choice == "16":
        counter.my_custom_feature()
```

### Creating a Feature Toggle

For features that can be toggled on/off:

```python
def toggle_my_feature(self):
    """Toggle my custom feature on/off"""
    current_state = self.config.get("my_feature_enabled", False)
    new_state = not current_state
    self.config["my_feature_enabled"] = new_state
    logger.info(f"My feature {'enabled' if new_state else 'disabled'}")
    self.save_config()
    return new_state
```

## Integrating with Other Apps

### Export Functionality

To integrate with other applications, you can expose functionality:

```python
class CounterAPI:
    """API wrapper for AutoCounter"""
    
    def __init__(self, counter):
        self.counter = counter
    
    def get_current_count(self):
        """Get current count value"""
        return self.counter.current_count
    
    def start_counting(self):
        """Start counting operation"""
        return self.counter.start_counting()
    
    def stop_counting(self):
        """Stop counting operation"""
        return self.counter.stop_counting()
    
    # Add additional API methods as needed
```

### Using as a Library

To use the counter as a library in another project:

```python
# Import the module
from auto_counter import AutoCounter

# Initialize
counter = AutoCounter(config_file="my_config.json")

# Setup accounts
counter.add_account("username", "token")

# Configure channel
counter.set_channel("channel_id")

# Start counting
counter.start_counting()

# Your application logic...
while running:
    # Check counter status
    status = counter.get_status()
    if status["error"]:
        handle_error(status["error"])
    
    # Do other things...
    time.sleep(1)
```

## Custom Message Formatting

### Basic Message Formatting

To customize message appearance:

```python
def custom_format_message(self, count):
    """Custom message formatter for counts"""
    # Basic formatting
    if count % 100 == 0:
        return f"**{count}** 🎉 Century!"
    elif count % 50 == 0:
        return f"**{count}** ✨ Half-century!"
    elif count % 10 == 0:
        return f"**{count}** 👍"
    else:
        return str(count)
        
# Set as formatter
counter.set_message_formatter(custom_format_message)
```

### Advanced Formatting with Templates

```python
# Template-based message system
templates = {
    "default": "{count}",
    "milestone": "**{count}** 🎉",
    "prime": "**{count}** 🔢 (prime!)",
    "funny": "**{count}** 😂"
}

def is_prime(n):
    """Check if number is prime"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def template_formatter(count):
    """Format message using templates"""
    # Special number handling
    funny_numbers = [69, 420, 666, 1337]
    
    if count in funny_numbers:
        return templates["funny"].format(count=count)
    elif count % 100 == 0:
        return templates["milestone"].format(count=count)
    elif is_prime(count):
        return templates["prime"].format(count=count)
    else:
        return templates["default"].format(count=count)
```

## Event Hooks

### Creating Hook System

Add an event hook system to allow custom triggers:

```python
class AutoCounter:
    def __init__(self, config_file="counter_config.json"):
        # ... existing initialization ...
        self.event_hooks = {
            "count_sent": [],
            "count_error": [],
            "reset_detected": [],
            "milestone_reached": []
        }
    
    def register_hook(self, event_name, callback):
        """Register a hook callback for an event"""
        if event_name in self.event_hooks:
            self.event_hooks[event_name].append(callback)
            logger.info(f"Registered hook for {event_name}")
            return True
        logger.warning(f"Unknown event: {event_name}")
        return False
    
    def trigger_hook(self, event_name, **kwargs):
        """Trigger all hooks for an event"""
        if event_name in self.event_hooks:
            for callback in self.event_hooks[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"Hook error ({event_name}): {e}")
```

### Using Hooks for Milestones

```python
# Register milestone hook
def milestone_hook(count, **kwargs):
    if count % 1000 == 0:
        # Do something special for thousands
        print(f"🏆 MAJOR MILESTONE: {count} 🏆")
        # Maybe send a webhook or notification
        send_webhook(f"Counter reached {count}!")

counter.register_hook("count_sent", milestone_hook)

# In the _counting_loop method
self.trigger_hook("count_sent", count=self.current_count, 
                  account=self.accounts[account_index].username)
```

## Custom Message Processing

### Custom Reset Detection

To implement custom reset detection logic:

```python
def custom_reset_detector(self, message):
    """Custom logic to detect channel resets"""
    # Look for special emoji patterns
    if "🔄" in message["content"] and "reset" in message["content"].lower():
        return True
        
    # Check for admin commands
    if message["author"]["id"] in self.admin_ids:
        if message["content"].startswith("!reset"):
            return True
            
    # Add your custom patterns here
    
    return False

# Register custom detector
counter.register_reset_detector(custom_reset_detector)
```

### Message Filter System

```python
class MessageFilter:
    """Filter system for processing messages"""
    
    def __init__(self):
        self.filters = []
    
    def add_filter(self, filter_func, priority=0):
        """Add a message filter with priority (higher runs first)"""
        self.filters.append({"func": filter_func, "priority": priority})
        self.filters.sort(key=lambda x: x["priority"], reverse=True)
    
    def process(self, messages):
        """Process messages through filter chain"""
        result = messages
        for filter_item in self.filters:
            result = filter_item["func"](result)
        return result

# Example filter functions
def remove_bot_messages(messages):
    """Filter out messages from bots"""
    return [msg for msg in messages if not msg.get("author", {}).get("bot", False)]
    
def only_number_messages(messages):
    """Only keep messages with valid numbers"""
    return [msg for msg in messages if msg["content"].strip().isdigit()]

# Setup filter chain
filter_system = MessageFilter()
filter_system.add_filter(remove_bot_messages, priority=10)
filter_system.add_filter(only_number_messages, priority=5)

# Use in scan_channel
filtered_messages = filter_system.process(messages)
```

## Custom Commands

### Adding Bot Commands

To add commands recognized in the counting channel:

```python
class CommandHandler:
    """Handle commands in the counting channel"""
    
    def __init__(self, counter):
        self.counter = counter
        self.commands = {}
        self.prefix = "!"
        
    def register_command(self, name, handler, help_text):
        """Register a new command"""
        self.commands[name] = {
            "handler": handler, 
            "help": help_text
        }
        
    def process_message(self, message):
        """Check if message is a command and process it"""
        if not message["content"].startswith(self.prefix):
            return False
            
        parts = message["content"][len(self.prefix):].split()
        if not parts:
            return False
            
        command = parts[0].lower()
        args = parts[1:]
        
        if command in self.commands:
            return self.commands[command]["handler"](
                message["author"], 
                args, 
                message
            )
        
        return False

# Example command handlers
def cmd_status(author, args, message):
    """Display status information"""
    current_count = counter.current_count
    is_counting = counter.counting_active
    
    response = f"Current count: {current_count}\nActive: {is_counting}"
    # Send response as a message
    counter.accounts[0].send_message(counter.channel_id, response)
    return True
    
def cmd_help(author, args, message):
    """Display help information"""
    help_text = "Available commands:\n"
    for cmd, data in command_handler.commands.items():
        help_text += f"`!{cmd}`: {data['help']}\n"
    
    counter.accounts[0].send_message(counter.channel_id, help_text)
    return True

# Setup command handler
command_handler = CommandHandler(counter)
command_handler.register_command("status", cmd_status, "Show counter status")
command_handler.register_command("help", cmd_help, "Show this help message")
```

## Performance Customization

### Custom Rate Limiting Strategy

To implement custom rate limit handling:

```python
class RateLimitStrategy:
    """Custom rate limiting strategy"""
    
    def __init__(self):
        self.rate_limit_history = []
        self.current_delay = 1.0  # seconds
        
    def record_rate_limit(self, retry_after, global_limit=False):
        """Record a rate limit event"""
        self.rate_limit_history.append({
            "time": time.time(),
            "retry": retry_after,
            "global": global_limit
        })
        
        # Trim history to last 20 events
        if len(self.rate_limit_history) > 20:
            self.rate_limit_history = self.rate_limit_history[-20:]
    
    def calculate_delay(self):
        """Calculate optimal delay based on history"""
        if not self.rate_limit_history:
            return max(0.5, self.current_delay * 0.9)  # Gradually decrease if no issues
            
        # Check if we've had recent rate limits (last 2 minutes)
        recent_limits = [
            r for r in self.rate_limit_history 
            if time.time() - r["time"] < 120
        ]
        
        if recent_limits:
            # Increase delay based on frequency and severity
            rate_limit_count = len(recent_limits)
            avg_retry = sum(r["retry"] for r in recent_limits) / rate_limit_count
            
            # More aggressive for global rate limits
            global_multiplier = 2.0 if any(r["global"] for r in recent_limits) else 1.0
            
            # Calculate new delay
            new_delay = self.current_delay * (1.0 + (0.2 * rate_limit_count * global_multiplier))
            self.current_delay = min(5.0, new_delay)  # Cap at 5 seconds
        else:
            # Gradually reduce delay if no recent issues
            self.current_delay = max(0.5, self.current_delay * 0.9)
            
        return self.current_delay

# Use the strategy
rate_strategy = RateLimitStrategy()

# When rate limited
def handle_rate_limit(retry_after, global_limit):
    rate_strategy.record_rate_limit(retry_after, global_limit)
    wait_time = retry_after + random.uniform(0.1, 0.5)
    time.sleep(wait_time)

# When sending next message
next_delay = rate_strategy.calculate_delay()
time.sleep(next_delay)
```

## Advanced Customization

### Custom Counting Algorithms

Create a pluggable system for different counting strategies:

```python
class CountingStrategy:
    """Base class for counting strategies"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def get_next_count(self, current_count, message_history):
        """Calculate next count based on strategy"""
        raise NotImplementedError("Subclasses must implement this")

class StandardCounting(CountingStrategy):
    """Standard incremental counting"""
    
    def __init__(self):
        super().__init__("standard", "Regular counting (1, 2, 3, ...)")
    
    def get_next_count(self, current_count, message_history):
        return current_count + 1

class FibonacciCounting(CountingStrategy):
    """Fibonacci sequence counting"""
    
    def __init__(self):
        super().__init__("fibonacci", "Fibonacci sequence (1, 1, 2, 3, 5, 8, ...)")
    
    def get_next_count(self, current_count, message_history):
        # If just starting, return 1
        if current_count == 0:
            return 1
            
        # Need at least two previous numbers
        if len(message_history) < 2:
            return 1
            
        # Extract the last two valid numbers
        nums = []
        for msg in message_history:
            content = msg["content"].strip()
            if content.isdigit():
                nums.append(int(content))
            if len(nums) >= 2:
                break
                
        if len(nums) >= 2:
            return nums[0] + nums[1]
            
        # Fallback
        return current_count + 1
        
# Register strategies
counting_strategies = {
    "standard": StandardCounting(),
    "fibonacci": FibonacciCounting()
}

# Use selected strategy
def get_next_count(self):
    strategy_name = self.config.get("counting_strategy", "standard")
    strategy = counting_strategies.get(strategy_name, counting_strategies["standard"])
    
    # Get message history for context-aware strategies
    messages = self.scan_channel(limit=5)
    
    return strategy.get_next_count(self.current_count, messages)
```

### Plugin System

For maximum flexibility, implement a plugin system:

```python
class CounterPlugin:
    """Base class for plugins"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.counter = None
    
    def initialize(self, counter):
        """Initialize plugin with counter instance"""
        self.counter = counter
        return True
        
    def on_count_sent(self, count, account):
        """Called when a count is sent"""
        pass
        
    def on_reset_detected(self, reason):
        """Called when reset is detected"""
        pass
        
    def on_start_counting(self):
        """Called when counting starts"""
        pass
        
    def on_stop_counting(self):
        """Called when counting stops"""
        pass

class PluginManager:
    """Manage counter plugins"""
    
    def __init__(self, counter):
        self.counter = counter
        self.plugins = {}
    
    def register_plugin(self, plugin):
        """Register a new plugin"""
        self.plugins[plugin.name] = plugin
        plugin.initialize(self.counter)
        logger.info(f"Registered plugin: {plugin.name}")
        return True
        
    def notify_all(self, event_name, **kwargs):
        """Notify all plugins of an event"""
        method_name = f"on_{event_name}"
        for name, plugin in self.plugins.items():
            if hasattr(plugin, method_name):
                try:
                    getattr(plugin, method_name)(**kwargs)
                except Exception as e:
                    logger.error(f"Plugin error ({name}.{method_name}): {e}")

# Example plugin
class StatisticsPlugin(CounterPlugin):
    """Track counting statistics"""
    
    def __init__(self):
        super().__init__("statistics", "Track counting statistics")
        self.count_history = []
        self.start_time = None
        
    def on_start_counting(self):
        self.start_time = time.time()
        
    def on_count_sent(self, count, account):
        self.count_history.append({
            "count": count,
            "time": time.time(),
            "account": account
        })
        
    def on_stop_counting(self):
        # Calculate statistics
        if not self.count_history or not self.start_time:
            return
            
        duration = time.time() - self.start_time
        count_count = len(self.count_history)
        counts_per_minute = count_count / (duration / 60)
        
        logger.info(f"Counting session statistics:")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Total counts: {count_count}")
        logger.info(f"Counts per minute: {counts_per_minute:.2f}")
        
        # Reset
        self.count_history = []
        self.start_time = None

# Setup plugin system
plugin_manager = PluginManager(counter)
plugin_manager.register_plugin(StatisticsPlugin())

# Notify plugins of events
def start_counting(self):
    # ... existing code ...
    self.plugin_manager.notify_all("start_counting")
    
def stop_counting(self):
    # ... existing code ...
    self.plugin_manager.notify_all("stop_counting")
```

## Debugging Your Extensions

### Debug Mode

Add a debug mode for easier extension development:

```python
def enable_debug_mode(self):
    """Enable debug mode for development"""
    self.debug_mode = True
    
    # Configure detailed logging
    logger.setLevel(logging.DEBUG)
    
    # Create console handler with formatting
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # Log API calls
    self.log_api_calls = True
    
    logger.debug("Debug mode enabled")
    
def debug_api_call(self, method, url, response_code=None, response_data=None):
    """Log API call for debugging"""
    if not self.log_api_calls:
        return
        
    logger.debug(f"API Call: {method} {url}")
    if response_code:
        logger.debug(f"Response: {response_code}")
    
    if response_data and self.log_api_responses:
        try:
            data_sample = str(response_data)[:100] + "..." if len(str(response_data)) > 100 else response_data
            logger.debug(f"Response data: {data_sample}")
        except:
            pass
```

### Monkey Patching

For quick testing without modifying source code:

```python
# Original method
original_send_message = DiscordAccount.send_message

# Monkey patch for debugging
def debug_send_message(self, channel_id, content):
    print(f"DEBUG: Sending message to {channel_id}: {content}")
    result = original_send_message(self, channel_id, content)
    print(f"DEBUG: Result: {result}")
    return result
    
# Apply monkey patch
DiscordAccount.send_message = debug_send_message

# For testing only - remove for production!
```

## Best Practices

When extending the bot, follow these best practices:

1. **Maintain Separation of Concerns**
   - Keep API interactions in DiscordAccount
   - Keep counting logic in AutoCounter
   - Keep UI in the main menu area

2. **Preserve Configuration Compatibility**
   - Add new config options with defaults
   - Verify your changes work with existing config files
   - Document new options

3. **Error Handling**
   - Add proper try/except blocks around all external API calls
   - Log exceptions with details
   - Fail gracefully when possible

4. **Performance Considerations**
   - Benchmark your changes
   - Consider the impact of added network requests
   - Test with realistic load
   
5. **Security First**
   - Never expose tokens
   - Validate all inputs
   - Consider rate limiting implications

6. **Documentation**
   - Add docstrings to all new methods
   - Update README.md with new features
   - Document any new config options

## Contributing Back

If you've extended the bot in useful ways, consider:

1. Cleaning up your code following the code style
2. Adding comprehensive tests
3. Ensuring backward compatibility
4. Submitting a pull request with a clear description
5. Including updated documentation

By following these guidelines, you can create powerful extensions that enhance the Discord Auto Counter while maintaining compatibility with the core code. 