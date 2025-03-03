#!/usr/bin/env python3
"""
Helper script for automatically approving terminal commands based on auto_commands.json configuration.
This script should be imported by Cursor IDE to check if a command can be auto-approved.
"""
import json
import os
import re
from pathlib import Path

def load_auto_commands_config():
    """Load the auto_commands.json configuration file."""
    config_path = Path(__file__).parent / 'auto_commands.json'
    
    if not config_path.exists():
        print("Warning: auto_commands.json not found.")
        return {"auto_approve_commands": {"patterns": []}}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: auto_commands.json is not valid JSON.")
        return {"auto_approve_commands": {"patterns": []}}

def should_auto_approve(command):
    """
    Check if a command should be automatically approved based on the configuration.
    
    Args:
        command: The command string to check
        
    Returns:
        bool: True if the command should be automatically approved, False otherwise
    """
    config = load_auto_commands_config()
    patterns = config.get("auto_approve_commands", {}).get("patterns", [])
    
    # Check if the command matches any of the patterns
    for pattern in patterns:
        # Convert the pattern to a regex pattern
        # Escape special characters in the pattern
        regex_pattern = pattern.replace("*", ".*")
        if re.match(f"^{regex_pattern}($|\\s)", command):
            return True
    
    return False

if __name__ == "__main__":
    # For testing purposes
    test_commands = [
        "python -m pytest",
        "python test_chess_app.py",
        "python app.py",
        "python -m unittest test_module",
        "pip install flask",  # This one should not be approved
        "rm -rf /",  # This one should not be approved
    ]
    
    print("Testing auto-approval for commands:")
    for cmd in test_commands:
        approved = should_auto_approve(cmd)
        print(f"{cmd}: {'✅ Auto-approved' if approved else '❌ Requires approval'}") 