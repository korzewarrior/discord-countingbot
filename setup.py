#!/usr/bin/env python
"""
Discord Auto Counter Bot Setup Script
This script helps new users get started with the Discord Auto Counter Bot
by setting up the initial configuration file.
"""

import os
import json
import shutil
import sys

def main():
    print("Discord Auto Counter Bot - Setup")
    print("-" * 40)
    
    # Check if configuration already exists
    if os.path.exists('counter_config.json'):
        print("Configuration file already exists.")
        overwrite = input("Do you want to create a new configuration? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled. Using existing configuration.")
            return
    
    # Check if template exists
    if not os.path.exists('counter_config.template.json'):
        print("Error: Template configuration file not found.")
        print("Make sure 'counter_config.template.json' is in the current directory.")
        return
    
    # Copy template to new configuration
    shutil.copy('counter_config.template.json', 'counter_config.json')
    print("Created new configuration file from template.")
    
    # Ask user if they want to configure now
    configure_now = input("Do you want to configure your Discord token now? (y/n): ").lower().strip()
    if configure_now != 'y':
        print("You can manually edit 'counter_config.json' later.")
        print("Setup complete!")
        return
    
    # Load configuration
    try:
        with open('counter_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Get channel ID
    channel_id = input("Enter Discord channel ID: ").strip()
    if channel_id:
        config['channel_id'] = channel_id
    
    # Account configuration
    print("\nAccount Setup:")
    print("You need at least one Discord account to use the bot.")
    
    config['accounts'] = []
    
    while True:
        username = input("\nEnter Discord username (or press Enter to finish): ").strip()
        if not username:
            break
            
        token = input("Enter Discord token: ").strip()
        user_agent = input("Enter user agent (or press Enter for default): ").strip()
        
        if not user_agent:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        account = {
            "username": username,
            "token": token,
            "user_agent": user_agent,
            "message_count": 0
        }
        
        config['accounts'].append(account)
        
        if len(config['accounts']) >= 1:
            another = input("Add another account? (y/n): ").lower().strip()
            if another != 'y':
                break
    
    # Save configuration
    try:
        with open('counter_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("\nConfiguration saved successfully!")
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return
    
    print("\nSetup complete! You can now run the bot with: python auto_counter.py")
    print("For more information, see the documentation in the docs/ directory.")

if __name__ == "__main__":
    main() 