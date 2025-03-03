#!/usr/bin/env python3
"""
Help script for the Genetic Chess Engine application.
This script provides detailed information about using the application.
"""
import os
import sys

def display_help():
    """Display detailed help information for the application."""
    print("\n" + "=" * 80)
    print("GENETIC CHESS ENGINE - HELP")
    print("=" * 80 + "\n")
    
    print("Welcome to the Genetic Chess Engine!")
    print("This application lets you play chess against an AI that evolves using genetic algorithms.\n")
    
    print("-" * 30)
    print("AVAILABLE COMMANDS")
    print("-" * 30)
    print("1. Start the application:")
    print("   ./start.py       - Menu-driven interface")
    print("   ./run.py         - Start the web app directly")
    print("   python3 app.py   - Start only the Flask server\n")
    
    print("2. Run tests:")
    print("   ./run_tests.py   - Run all tests")
    print("   python3 test_chess_app.py - Run only backend tests\n")
    
    print("3. Get help:")
    print("   ./help.py        - Display this help information\n")
    
    print("4. Troubleshooting:")
    print("   ./troubleshoot.py - Run diagnostics for connection issues\n")
    
    print("-" * 30)
    print("SERVER CONFIGURATION")
    print("-" * 30)
    print("You can configure the server using environment variables:")
    print("   PORT=8080 python3 app.py  - Change the port to 8080")
    print("   HOST=127.0.0.1 python3 app.py - Bind only to localhost")
    print("   DEBUG=true python3 app.py - Enable debug mode\n")
    print("Or use the start.py menu to configure settings interactively.\n")
    
    print("-" * 30)
    print("HOW TO PLAY")
    print("-" * 30)
    print("1. Start the application using one of the commands above")
    print("2. Open your web browser to http://localhost:5000 (if not opened automatically)")
    print("3. Choose a difficulty level (Easy, Medium, Hard)")
    print("4. Click 'New Game' to start a game")
    print("5. Make moves by clicking and dragging pieces")
    print("6. The AI will respond with its own moves\n")
    
    print("-" * 30)
    print("EVOLVING THE AI")
    print("-" * 30)
    print("1. Click 'Evolve AI' during a game")
    print("2. Choose the number of generations (more generations = longer evolution)")
    print("3. Click 'Confirm' to start evolution")
    print("4. Wait for the process to complete")
    print("5. Start a new game to play against the improved AI\n")
    
    print("-" * 30)
    print("ADDITIONAL INFORMATION")
    print("-" * 30)
    print("- Source code: See the README.md file for more details")
    print("- Documentation: Code is documented with comments")
    print("- License: MIT License\n")
    
    print("-" * 30)
    print("TROUBLESHOOTING")
    print("-" * 30)
    print("If you have trouble connecting to the server:")
    print("1. Make sure port 5000 is not in use by another application")
    print("2. Try using a different port: PORT=8080 python3 app.py")
    print("3. Check your firewall settings")
    print("4. Run ./troubleshoot.py for detailed diagnostics\n")

if __name__ == "__main__":
    display_help()
    sys.exit(0) 