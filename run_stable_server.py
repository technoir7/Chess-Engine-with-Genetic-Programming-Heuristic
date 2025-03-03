#!/usr/bin/env python3
"""
Run the Genetic Chess Engine server with keep-alive functionality.
This script starts the keep-alive monitor in the background and
provides a clean way to stop it when needed.
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from datetime import datetime

# Default settings
DEFAULT_PORT = 5001
DEFAULT_HOST = "0.0.0.0"
DEFAULT_DEBUG = False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Genetic Chess Engine server with keep-alive functionality")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST,
                        help=f"Host to bind the server to (default: {DEFAULT_HOST})")
    parser.add_argument("--debug", action="store_true", default=DEFAULT_DEBUG,
                        help="Run server in debug mode")
    return parser.parse_args()

def check_prerequisites():
    """Check that all necessary files and scripts exist."""
    # Check for keep-alive script
    if not os.path.exists("server_keep_alive.sh"):
        print("Error: server_keep_alive.sh not found in the current directory.")
        print("Please make sure you are in the correct directory.")
        return False
    
    # Check for app.py
    if not os.path.exists("app.py"):
        print("Error: app.py not found in the current directory.")
        print("Please make sure you are in the correct directory.")
        return False
    
    # Check if keep-alive script is executable
    if not os.access("server_keep_alive.sh", os.X_OK):
        print("Making server_keep_alive.sh executable...")
        try:
            os.chmod("server_keep_alive.sh", 0o755)
        except Exception as e:
            print(f"Error making script executable: {e}")
            return False
    
    return True

def check_environment():
    """Check for problematic environment variables and warn the user."""
    problematic_vars = []
    
    if 'PYTHONHOME' in os.environ and '.mount_cursor' in os.environ.get('PYTHONHOME', ''):
        problematic_vars.append('PYTHONHOME')
    
    if 'PYTHONPATH' in os.environ and '.mount_cursor' in os.environ.get('PYTHONPATH', ''):
        problematic_vars.append('PYTHONPATH')
    
    if problematic_vars:
        print("\n⚠️ Warning: Detected potentially problematic environment variables:")
        for var in problematic_vars:
            print(f"  - {var}={os.environ.get(var)}")
        print("\nThe keep-alive script will automatically clear these variables before starting the server.")
        print("If you encounter issues, you may want to manually clear them in your current shell:")
        for var in problematic_vars:
            print(f"  unset {var}")
        print()
    
    return True

def start_server(port, host, debug):
    """Start the server with keep-alive functionality."""
    print(f"Starting Genetic Chess Engine server on {host}:{port} (debug={debug})...")
    
    # Check environment
    check_environment()
    
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["HOST"] = host
    env["DEBUG"] = "true" if debug else "false"
    
    # Start the keep-alive process
    try:
        process = subprocess.Popen(
            ["./server_keep_alive.sh"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"Server keep-alive monitor started with PID: {process.pid}")
        print("The server will be automatically restarted if it crashes.")
        print("Press Ctrl+C to stop the server and exit.")
        
        # Print logs in real-time
        try:
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(line.rstrip())
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Shutting down...")
            # Send SIGTERM to the process group
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except:
                # Fallback to just killing the process
                process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
                print("Server stopped successfully.")
            except subprocess.TimeoutExpired:
                print("Server did not stop gracefully, forcing termination...")
                process.kill()
        
        return True
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def main():
    """Main function to run the server."""
    print(f"=== Genetic Chess Engine Server Launcher ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    args = parse_args()
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not start_server(args.port, args.host, args.debug):
        sys.exit(1)
    
    print("Server has been shut down.")

if __name__ == "__main__":
    main() 