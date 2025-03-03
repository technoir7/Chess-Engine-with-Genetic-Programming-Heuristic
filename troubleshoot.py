#!/usr/bin/env python3
"""
Troubleshooting script for the Genetic Chess Engine.
This script helps diagnose connection issues with the Flask application.
"""

import os
import sys
import socket
import subprocess
import platform
import time

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the header for the troubleshooting tool."""
    print("\n" + "=" * 80)
    print(f"{'GENETIC CHESS ENGINE - TROUBLESHOOTING TOOL':^80}")
    print("=" * 80 + "\n")

def check_python_version():
    """Check and display the Python version."""
    print("Python Version:")
    print(f"  {sys.version}")
    print(f"  Executable: {sys.executable}\n")

def check_flask_installed():
    """Check if Flask is installed."""
    print("Checking Flask installation:")
    try:
        import flask
        print(f"  Flask is installed (version {flask.__version__})")
        flask_ok = True
    except ImportError:
        print("  Flask is NOT installed! Please run: pip install -r requirements.txt")
        flask_ok = False
    print()
    return flask_ok

def check_port_available():
    """Check if port 5000 is available."""
    print("Checking if port 5000 is available:")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", 5000))
        print("  Port 5000 is available")
        port_available = True
    except socket.error:
        print("  Port 5000 is in use by another process!")
        port_available = False
    finally:
        s.close()
    print()
    return port_available

def check_network_interfaces():
    """Check and display network interfaces."""
    print("Network interfaces:")
    
    # Different commands for different platforms
    if platform.system() == "Windows":
        result = subprocess.run("ipconfig", capture_output=True, text=True, shell=True)
    else:
        result = subprocess.run("ifconfig || ip addr", capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        # Just show localhost interfaces for simplicity
        for line in result.stdout.split('\n'):
            if '127.0.0.1' in line or 'localhost' in line:
                print(f"  {line.strip()}")
    else:
        print("  Unable to retrieve network interfaces")
    print()

def test_flask_app():
    """Test starting the Flask app and check if it's responding."""
    print("Testing Flask application:")
    
    # Start the Flask app in a separate process
    print("  Starting Flask app in the background...")
    
    if platform.system() == "Windows":
        flask_process = subprocess.Popen(
            ["python", "app.py"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        flask_process = subprocess.Popen(
            ["python3", "app.py"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
    
    # Wait for the app to start
    print("  Waiting for the app to start (5 seconds)...")
    time.sleep(5)
    
    # Try to connect to the app
    print("  Testing connection to http://localhost:5000...")
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:5000/", timeout=5)
        status = response.status
        print(f"  Connection successful! Status code: {status}")
    except Exception as e:
        print(f"  Connection failed: {str(e)}")
    
    # Try to connect to 127.0.0.1 explicitly
    print("  Testing connection to http://127.0.0.1:5000...")
    try:
        import urllib.request
        response = urllib.request.urlopen("http://127.0.0.1:5000/", timeout=5)
        status = response.status
        print(f"  Connection successful! Status code: {status}")
    except Exception as e:
        print(f"  Connection failed: {str(e)}")
        
    # Terminate the Flask process
    print("  Stopping Flask app...")
    if platform.system() == "Windows":
        flask_process.terminate()
    else:
        import signal
        os.killpg(os.getpgid(flask_process.pid), signal.SIGTERM)
    
    # Get any output from the process
    stdout, stderr = flask_process.communicate()
    if stdout:
        print("\nApp stdout:")
        print(stdout.decode('utf-8'))
    if stderr:
        print("\nApp stderr:")
        print(stderr.decode('utf-8'))
    
    print()

def suggest_solutions(flask_ok, port_available):
    """Suggest solutions based on the diagnosis."""
    print("=" * 80)
    print("TROUBLESHOOTING SUGGESTIONS")
    print("=" * 80)
    
    if not flask_ok:
        print("1. Install Flask and other dependencies:")
        print("   pip install -r requirements.txt")
        print("   -- or --")
        print("   pip3 install -r requirements.txt\n")
    
    if not port_available:
        print("2. Port 5000 is already in use. Options:")
        print("   - Find and stop the process using port 5000")
        print("   - Modify app.py to use a different port (e.g., 5001)\n")
    
    print("3. If you still can't connect to localhost:")
    print("   - Try accessing the app directly at http://127.0.0.1:5000")
    print("   - Check your firewall settings")
    print("   - Make sure your browser is not using a proxy\n")
    
    print("4. Try starting the app with:")
    print("   python3 -m flask --app app run --host=0.0.0.0 --port=5000\n")
    
    print("5. If all else fails, check the Flask documentation:")
    print("   https://flask.palletsprojects.com/\n")

def main():
    """Main function to run all diagnostic checks."""
    clear_screen()
    print_header()
    
    check_python_version()
    flask_ok = check_flask_installed()
    port_available = check_port_available()
    check_network_interfaces()
    
    try:
        test_flask_app()
    except Exception as e:
        print(f"Error testing Flask app: {e}\n")
    
    suggest_solutions(flask_ok, port_available)
    
    print("\nTroubleshooting complete!")
    print("If this tool didn't resolve your issue, please contact support.\n")

if __name__ == "__main__":
    main() 