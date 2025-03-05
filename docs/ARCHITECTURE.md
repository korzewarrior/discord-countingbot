# Discord Auto Counter - System Architecture

## High-Level Architecture
The Discord Auto Counter follows a modular design with two primary classes:
1. **DiscordAccount**: Manages individual Discord accounts, handling authentication and API interactions
2. **AutoCounter**: Core controller that manages accounts, scan operations, and counting logic

```
[System Architecture Diagram]

Discord Channel <---> AutoCounter (Controller)
                     /           \
                    /             \
       DiscordAccount 1     DiscordAccount 2
       (API Client)         (API Client)
```

## Core Components

### DiscordAccount Component
Responsible for:
- Managing authentication for a single Discord user
- Sending messages to Discord channels
- Retrieving messages from Discord channels
- Managing API rate limits for the account
- Simulating typing indicators

### AutoCounter Controller
Responsible for:
- Managing multiple DiscordAccount instances
- Coordinating which account sends the next count
- Scanning channel to determine current count
- Detecting reset messages from Discord bots
- Auto-restarting after resets
- Managing counting speed and delays
- Handling configuration loading/saving

### Threading Model
The system uses Python's threading to:
- Run the counting loop in a background thread
- Allow the main thread to handle user interface interactions
- Ensure counting continues while users interact with the menu

### Configuration System
- Uses JSON for persistent storage
- Stores account credentials, current count, and settings
- Saves state automatically during operation to survive crashes

### Event Flow

1. **Initialization**:
   - Load configuration from JSON
   - Initialize account objects
   - Set up initial state

2. **Scanning Process**:
   - Retrieve recent messages from the channel
   - Parse messages to find latest numbers
   - Check for reset messages from counting bots
   - Update internal state based on findings

3. **Counting Process**:
   - Select next account to send a message
   - Calculate appropriate delay
   - Send the next number in sequence
   - Update internal state
   - Save configuration

4. **Reset Handling**:
   - Detect reset messages in real-time
   - Reset count to 0
   - Wait for cooldown
   - Auto-restart counting from 1

5. **Network Management**:
   - Detect connection issues
   - Attempt reconnection
   - Reset sessions if needed
   - Continue operation once connection is restored

## Design Patterns

### Observer Pattern
- The scanning system observes the Discord channel for changes
- When reset messages are detected, observers are notified

### Strategy Pattern
- Different counting strategies (normal, speed mode, ludicrous mode)
- Configurable parameters for customizing behavior

### Factory Pattern
- Account creation and management
- Configuration system for creating consistent state

### Command Pattern
- Menu system for user interactions
- Command-line arguments for automated control 