# Discord Auto Counter - Coding Standards

This document outlines the coding standards and best practices for contributing to the Discord Auto Counter project. Following these guidelines ensures code quality, maintainability, and consistency across the codebase.

## Code Style

### Python Version
- Use Python 3.7+ compatible code
- Avoid syntax or features that require newer Python versions

### PEP 8 Compliance
Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:
- 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters
- Two blank lines before top-level class and function definitions
- One blank line before method definitions within a class
- Use snake_case for functions, methods, and variables
- Use CamelCase for classes
- Use UPPER_CASE for constants

### Imports
- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application imports
- Separate each group with a blank line
- Prefer explicit imports over wildcard imports

```python
# Good
import json
import logging
import time
from datetime import datetime, timedelta

import requests

from utils import format_timestamp
from .constants import DEFAULT_TIMEOUT
```

### String Formatting
- Use f-strings for string formatting when Python 3.6+ is guaranteed
- Use .format() as a fallback for complex formatting
- Avoid % formatting

```python
# Good
username = "counter_bot"
count = 42
log_message = f"User {username} sent count: {count}"

# For complex formatting
complex_format = "Count: {count:05d} | Rate: {rate:.2f}/sec".format(
    count=current_count, 
    rate=messages_per_second
)
```

## Documentation

### Docstrings
- All modules, classes, and functions should have docstrings
- Use the Google-style docstring format

```python
def scan_channel(self, limit=30):
    """Scan channel for current count and last counter.
    
    Retrieves recent messages from the channel and analyzes them to
    determine the current count and who last contributed.
    
    Args:
        limit (int): Maximum number of messages to retrieve.
        
    Returns:
        tuple: (success, result) where result contains the scan results.
        
    Example:
        success, result = counter.scan_channel(limit=50)
        if success:
            print(f"Current count: {result['current_count']}")
    """
```

### Comments
- Use comments to explain "why", not "what"
- Add TODO comments for planned improvements (include GitHub issue if applicable)
- Use complete sentences with proper capitalization and punctuation

```python
# Good
# Skip messages from bots to avoid counting bot commands
if message.get("author", {}).get("bot", False):
    continue

# Bad - states the obvious
# This increments the count
count += 1
```

## Code Organization

### File Structure
- Keep files focused on a single responsibility
- Generally aim for files under 500 lines
- Use descriptive file names that reflect their purpose

### Class and Function Design
- Classes should have a single responsibility
- Functions should do one thing and do it well
- Maximum function length ~50 lines; consider refactoring longer functions
- Limit function parameters to ~5; use data classes or dictionaries for more

### Error Handling
- Use explicit exception types, not bare `except:`
- Handle exceptions at the appropriate level
- Log exceptions with contextual information
- Provide meaningful error messages

```python
# Good
try:
    response = session.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
except requests.exceptions.Timeout:
    logger.error(f"Request timed out: {url}")
    return False, {"error": "timeout"}
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error {e.response.status_code}: {url}")
    return False, {"error": f"http_error_{e.response.status_code}"}
except Exception as e:
    logger.error(f"Unexpected error requesting {url}: {str(e)}")
    return False, {"error": "unknown", "details": str(e)}
```

## Performance Considerations

### Network Operations
- Use connection pooling (session reuse)
- Implement proper timeout handling
- Cache frequently accessed data
- Minimize API calls

```python
# Good - reuse session
self.session = requests.Session()
self.session.headers.update({
    "Authorization": self.token,
    "User-Agent": self.user_agent
})

# Make requests with timeout
response = self.session.get(url, timeout=10.0)
```

### Resource Management
- Close resources (file handles, network connections) properly
- Use context managers (`with` statements) when appropriate
- Be mindful of memory usage with large data structures

```python
# Good
with open(self.config_file, 'w') as f:
    json.dump(self.config, f, indent=2)
```

### Concurrency
- Use threading for I/O-bound operations
- Ensure thread safety with proper locks
- Avoid global state in threaded code

```python
# Thread safety for configuration access
def save_config(self):
    """Save configuration to file (thread-safe)"""
    with self.config_lock:
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
```

## Security Best Practices

### Sensitive Data Handling
- Never hardcode tokens, passwords, or secrets
- Sanitize logs to remove sensitive information
- Use environment variables or secure config files

```python
# Good
def log_request(self, url, method, status_code=None):
    """Log API request with sensitive data redacted."""
    # Redact token from URL if present
    safe_url = url.replace(self.token, "[REDACTED]") if self.token in url else url
    if status_code:
        logger.debug(f"{method} {safe_url} - {status_code}")
    else:
        logger.debug(f"{method} {safe_url}")
```

### Input Validation
- Validate all user inputs
- Use safe defaults
- Implement proper access controls

```python
# Good
def set_messages_per_second(self, value):
    """Set message rate with validation."""
    try:
        rate = float(value)
        if rate <= 0:
            logger.warning("Invalid rate (must be positive): %s", value)
            return False
        if rate > MAX_SAFE_RATE and not self.config.get("acknowledged_high_risk", False):
            logger.warning("Rate exceeds safe maximum (%s). Use acknowledge_high_risk() first.", MAX_SAFE_RATE)
            return False
        
        self.config["messages_per_second"] = min(rate, ABSOLUTE_MAX_RATE)
        self.save_config()
        return True
    except (ValueError, TypeError):
        logger.warning("Invalid rate value: %s", value)
        return False
```

## Testing

### Unit Tests
- Write unit tests for all public functions
- Aim for high test coverage
- Use descriptive test names that explain the test case

```python
def test_extract_count_from_valid_message():
    """Test count extraction from a valid message string."""
    # Arrange
    message = {"content": "42", "author": {"id": "12345"}}
    counter = AutoCounter()
    
    # Act
    result = counter._extract_count_from_message(message)
    
    # Assert
    assert result == 42
```

### Mocking
- Use mocks for external dependencies (API calls, file I/O)
- Create realistic test fixtures
- Test error conditions and edge cases

```python
@patch('requests.Session')
def test_send_message_handles_timeout(mock_session):
    """Test that send_message properly handles timeouts."""
    # Arrange
    mock_session.return_value.post.side_effect = requests.exceptions.Timeout("Connection timed out")
    account = DiscordAccount("test", "token")
    
    # Act
    success, result = account.send_message("123", "test message")
    
    # Assert
    assert not success
    assert "timeout" in result["error"]
```

## Version Control Practices

### Commits
- Write clear commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers when applicable
- Keep commits focused on a single change

### Branching
- Use feature branches for development
- Name branches descriptively (e.g., `feature/auto-restart` or `fix/rate-limit-handling`)
- Keep branches up to date with the main branch

### Pull Requests
- Include a clear description of changes
- Link to relevant issues
- Ensure all tests pass
- Address review comments promptly

## Logging

### Logging Levels
Use appropriate logging levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: Confirmation that things are working as expected
- `WARNING`: Indication that something unexpected happened
- `ERROR`: An error occurred but execution can continue
- `CRITICAL`: A serious error that may prevent program execution

```python
# Configure logging with clear level usage
def setup_logging(self, log_level="INFO"):
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger("counter_bot")
    logger.setLevel(numeric_level)
    
    # Example usage
    logger.debug("Detailed debug information")
    logger.info("Bot started successfully")
    logger.warning("Rate limit approaching threshold")
    logger.error("Failed to send message: timeout")
    logger.critical("Authentication failed - cannot continue")
```

### Log Messages
- Include contextual information in log messages
- Format log messages for easy filtering and analysis
- Be consistent in log message formatting

```python
# Good log message pattern
logger.info(f"Sending count {count} to channel {channel_id} using account {account_name}")
```

## Configuration Management

### Default Configuration
- Provide sensible defaults for all settings
- Document configuration options
- Validate configuration on load

```python
def load_config(self):
    """Load configuration with defaults for missing values."""
    try:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
            
        # Apply defaults
        self.config.setdefault("messages_per_second", 1.0)
        self.config.setdefault("verify_last_message", True)
        self.config.setdefault("speed_mode", False)
        self.config.setdefault("scan_interval", 30)
        self.config.setdefault("current_count", 0)
        self.config.setdefault("human_mode", True)
        
        return True
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        self.config = {}
        return False
```

### Configuration Versioning
- Include version information in configuration files
- Implement migration logic for configuration changes
- Maintain backward compatibility when possible

```python
def migrate_config(self):
    """Migrate configuration to latest version."""
    config_version = self.config.get("version", "1.0")
    
    if config_version == "1.0":
        # Migrate from 1.0 to 1.1
        self.config["human_mode"] = self.config.get("simulate_typing", True)
        if "simulate_typing" in self.config:
            del self.config["simulate_typing"]
        self.config["version"] = "1.1"
        
    if config_version < "1.2":
        # Migrate from 1.1 to 1.2
        if "accounts" in self.config:
            self.config["accounts"] = [
                {"username": a.get("username"), "token": a.get("token")} 
                for a in self.config["accounts"]
            ]
        self.config["version"] = "1.2"
    
    # Save migrated config
    self.save_config()
```

## Dependencies

### Managing Dependencies
- Keep dependencies to a minimum
- Specify version requirements in requirements.txt
- Document dependency purpose and usage

```
# requirements.txt with explanations
# HTTP requests library for Discord API interaction
requests==2.28.1

# Date parsing for message timestamps
python-dateutil==2.8.2
```

### Vendoring
- Consider vendoring small dependencies to reduce external requirements
- Document the source and license of any vendored code
- Keep vendored code in a separate directory

## API Design

### Method Signatures
- Use descriptive method names
- Use keyword arguments for clarity and future compatibility
- Return consistent data structures

```python
# Good method design
def scan_channel(self, limit=30, include_bot_messages=False, 
                max_age_minutes=None):
    """Scan channel for current count and last counter."""
    # ...implementation...
    
    return success, {
        "current_count": current_count,
        "last_counter_id": last_counter_id,
        "last_counter_name": last_counter_name,
        "message_count": len(messages),
        "timestamp": datetime.now().isoformat()
    }
```

### Return Values
- Return consistent types
- Use named tuples or dictionaries for complex returns
- Include success/failure indication in return values

```python
# Consistent return pattern
def send_message(self, channel_id, content):
    """Send message to Discord channel.
    
    Returns:
        tuple: (success, result) where:
            - success (bool): Whether the operation succeeded
            - result (dict): Contains details about the operation
    """
    try:
        # ... implementation ...
        return True, {"message_id": message_id, "timestamp": timestamp}
    except Exception as e:
        return False, {"error": str(e)}
```

## Release Management

### Versioning
- Follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- Update version number in code and documentation
- Maintain a changelog

### Release Process
- Tag releases in version control
- Include release notes
- Update documentation for new releases

## Conclusion

By adhering to these coding standards, we maintain a high-quality, maintainable, and secure codebase. These guidelines help ensure that all contributors can effectively work with the code and that the project remains robust and reliable for its users.

Remember that these standards are meant to guide development, not restrict it. Use good judgment, and when in doubt, prioritize readability and maintainability. 