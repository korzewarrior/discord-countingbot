#!/usr/bin/env python
"""
Discord Auto Counter - Configuration Cleaner

This utility helps users clean sensitive data from their configuration files
before sharing for troubleshooting or bug reports.
"""

import os
import json
import argparse
import sys

def clean_config(input_file, output_file):
    """Clean sensitive data from a configuration file."""
    try:
        with open(input_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False
    
    # Clean sensitive data
    if 'channel_id' in config:
        config['channel_id'] = "CHANNEL_ID_REMOVED"
    
    if 'accounts' in config:
        for account in config['accounts']:
            if 'username' in account:
                account['username'] = "USERNAME_REMOVED"
            if 'token' in account:
                account['token'] = "TOKEN_REMOVED"
            if 'user_agent' in account:
                account['user_agent'] = "USER_AGENT_REMOVED"
    
    # Save cleaned configuration
    try:
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Cleaned configuration saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Clean sensitive data from configuration files')
    parser.add_argument('--input', '-i', default='counter_config.json',
                        help='Input configuration file (default: counter_config.json)')
    parser.add_argument('--output', '-o', default='counter_config.clean.json',
                        help='Output configuration file (default: counter_config.clean.json)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    print(f"Cleaning configuration from {args.input} to {args.output}")
    success = clean_config(args.input, args.output)
    
    if success:
        print("\nConfiguration cleaned successfully!")
        print("You can now safely share this file for troubleshooting.")
        print(f"File location: {os.path.abspath(args.output)}")
        return 0
    else:
        print("\nFailed to clean configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 