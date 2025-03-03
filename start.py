#!/usr/bin/env python3
"""
Start script for the Genetic Chess Engine application.
This script provides a menu with all available commands for the application.
"""

import os
import sys
import subprocess
import webbrowser
from threading import Timer

# Determine the Python executable to use
PYTHON_EXECUTABLE = sys.executable

# Default configuration
DEFAULT_PORT = 5000
DEFAULT_HOST = '0.0.0.0'

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
    print("4. Configure server settings")
    print("5. Run troubleshooting tool")
    print("6. Exit")
    print("\n" + "-" * 80 + "\n")

def get_current_config():
    """Get current configuration from environment variables."""
    port = os.environ.get('PORT', DEFAULT_PORT)
    host = os.environ.get('HOST', DEFAULT_HOST)
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', 't', '1')
    return port, host, debug

def set_environment_variables(port, host, debug):
    """Set environment variables for the application."""
    os.environ['PORT'] = str(port)
    os.environ['HOST'] = host
    os.environ['DEBUG'] = str(debug).lower()

def configure_settings():
    """Configure server settings."""
    clear_screen()
    print_header()
    
    # Get current settings
    current_port, current_host, current_debug = get_current_config()
    
    print("CONFIGURE SERVER SETTINGS\n")
    print(f"Current settings:")
    print(f"  - Port: {current_port}")
    print(f"  - Host: {current_host}")
    print(f"  - Debug mode: {'Enabled' if current_debug else 'Disabled'}")
    print("\n" + "-" * 40 + "\n")
    
    # Get new settings
    try:
        # Port
        port_input = input(f"Enter port number (default: {current_port}): ").strip()
        if port_input:
            port = int(port_input)
        else:
            port = int(current_port)
        
        # Host
        host_input = input(f"Enter host (default: {current_host}): ").strip()
        host = host_input if host_input else current_host
        
        # Debug mode
        debug_input = input(f"Enable debug mode? (y/n) (default: {'y' if current_debug else 'n'}): ").strip().lower()
        if debug_input:
            debug = debug_input in ('y', 'yes', 'true')
        else:
            debug = current_debug
        
        # Set environment variables
        set_environment_variables(port, host, debug)
        
        print("\nSettings updated successfully!")
        print(f"The server will now run on {host}:{port} with debug mode {'enabled' if debug else 'disabled'}")
        input("\nPress Enter to return to the main menu...")
    except ValueError:
        print("\nInvalid port number. Please enter a valid integer.")
        input("\nPress Enter to return to the main menu...")

def start_application():
    """Start the Flask server and open the application in a web browser."""
    clear_screen()
    print_header()
    print("Starting the application...\n")
    
    # Get current settings
    port, host, debug = get_current_config()
    
    # Function to open browser after a short delay
    def open_browser():
        url = f'http://localhost:{port}'
        webbrowser.open(url)
        print(f"Web browser opened to {url}")
    
    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Print instructions
    print(f"The Flask server is starting on {host}:{port} with debug mode {'enabled' if debug else 'disabled'}")
    print("A browser window will open automatically.")
    print("Press Ctrl+C to stop the server when you're done.\n")
    
    # Start the Flask server using the run.sh script
    try:
        subprocess.run(["./run.sh"])
    except KeyboardInterrupt:
        print("\nServer stopped.")

def run_tests():
    """Run all tests for the application."""
    clear_screen()
    print_header()
    print("Running all tests...\n")
    
    try:
        subprocess.run([PYTHON_EXECUTABLE, 'run_tests.py'])
        input("\nPress Enter to return to the main menu...")
    except KeyboardInterrupt:
        print("\nTest execution stopped.")

def show_help():
    """Show help information."""
    clear_screen()
    print_header()
    print("Showing help information...\n")
    
    try:
        subprocess.run([PYTHON_EXECUTABLE, 'help.py'])
        input("\nPress Enter to return to the main menu...")
    except KeyboardInterrupt:
        print("\nHelp display stopped.")

def run_troubleshooting():
    """Run the troubleshooting tool."""
    clear_screen()
    print_header()
    print("Running troubleshooting tool...\n")
    
    try:
        subprocess.run([PYTHON_EXECUTABLE, 'troubleshoot.py'])
        input("\nPress Enter to return to the main menu...")
    except KeyboardInterrupt:
        print("\nTroubleshooting stopped.")

def main():
    """Main function to run the menu-driven interface."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            start_application()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            show_help()
        elif choice == '4':
            configure_settings()
        elif choice == '5':
            run_troubleshooting()
        elif choice == '6':
            clear_screen()
            print_header()
            print("Exiting Genetic Chess Engine. Goodbye!\n")
            sys.exit(0)
        else:
            input("Invalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main() 