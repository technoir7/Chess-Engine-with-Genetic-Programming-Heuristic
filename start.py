#!/usr/bin/env python
"""
Start script for the Genetic Chess Engine application.
This script provides a menu with all available commands for the application.
"""

import os
import sys
import subprocess
import webbrowser
from threading import Timer

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("\n" + "=" * 80)
    print(f"{'GENETIC CHESS ENGINE':^80}")
    print("=" * 80)
    print(f"{'An AI chess engine that evolves using genetic algorithms':^80}")
    print("-" * 80 + "\n")

def print_menu():
    """Print the main menu."""
    print("AVAILABLE COMMANDS:\n")
    print("1. Start the application (run Flask server)")
    print("2. Run all tests (Python backend and JavaScript frontend)")
    print("3. View help information")
    print("4. Exit")
    print("\n" + "-" * 80 + "\n")

def start_application():
    """Start the Flask server and open the application in a web browser."""
    clear_screen()
    print_header()
    print("Starting the application...\n")
    
    # Function to open browser after a short delay
    def open_browser():
        webbrowser.open('http://localhost:5000')
        print("Web browser opened to http://localhost:5000")
    
    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Print instructions
    print("The Flask server is starting. A browser window will open automatically.")
    print("Press Ctrl+C to stop the server when you're done.\n")
    
    # Start the Flask server
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\nServer stopped.")

def run_tests():
    """Run all tests for the application."""
    clear_screen()
    print_header()
    print("Running all tests...\n")
    
    try:
        subprocess.run([sys.executable, 'run_tests.py'])
        input("\nPress Enter to return to the main menu...")
    except KeyboardInterrupt:
        print("\nTest execution stopped.")

def show_help():
    """Show help information."""
    clear_screen()
    print_header()
    print("Showing help information...\n")
    
    try:
        subprocess.run([sys.executable, 'help.py'])
        input("\nPress Enter to return to the main menu...")
    except KeyboardInterrupt:
        print("\nHelp display stopped.")

def main():
    """Main function to run the menu-driven interface."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            start_application()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            show_help()
        elif choice == '4':
            clear_screen()
            print_header()
            print("Exiting Genetic Chess Engine. Goodbye!\n")
            sys.exit(0)
        else:
            input("Invalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main() 