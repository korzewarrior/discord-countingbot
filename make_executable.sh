#!/bin/bash
# Make Python scripts executable

echo "Making Python scripts executable..."

# Main scripts
chmod +x auto_counter.py
chmod +x setup.py
chmod +x scripts/*.py

echo "Done!"
echo "You can now run the bot with './auto_counter.py' instead of 'python auto_counter.py'" 