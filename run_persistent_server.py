#!/usr/bin/env python3
"""
Persistent Server for Genetic Chess Engine

This script provides a robust way to run the Flask application with automatic
restart capabilities and proper environment handling. It monitors the server
process and restarts it if it crashes or becomes unresponsive.

Features:
- Clears problematic environment variables
- Uses Gunicorn if available (falls back to Flask development server)
- Continuously monitors server health
- Automatic restart if server crashes or becomes unresponsive
- Comprehensive logging
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import logging
import threading
import requests
from datetime import datetime

# Default configuration
DEFAULT_PORT = 5001
DEFAULT_HOST = "127.0.0.1"  # More secure than 0.0.0.0 for local development
DEFAULT_CHECK_INTERVAL = 5  # seconds
DEFAULT_MAX_RESTARTS = 10
DEFAULT_TIMEOUT = 10  # seconds

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("persistent_server.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global variables
server_process = None
restart_count = 0
running = True


def clean_environment():
    """Remove problematic environment variables that could interfere with Python."""
    problematic_vars = [
        "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", 
        "PYTHONUSERBASE", "PYTHONEXECUTABLE"
    ]
    
    for var in problematic_vars:
        if var in os.environ:
            logger.info(f"Unsetting {var}={os.environ[var]}")
            del os.environ[var]
    
    return {var: os.environ.get(var) for var in problematic_vars if os.environ.get(var)}


def check_server_health(host, port, timeout=DEFAULT_TIMEOUT):
    """Check if the server is responding to HTTP requests."""
    url = f"http://{host}:{port}/"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True
        logger.warning(f"Server responded with status code: {response.status_code}")
        return False
    except requests.RequestException as e:
        logger.warning(f"Server health check failed: {e}")
        return False


def has_gunicorn():
    """Check if gunicorn is available."""
    try:
        subprocess.run(
            ["gunicorn", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def start_server(host, port, debug=False, use_gunicorn=True):
    """Start the Flask application server."""
    global server_process
    
    # Clear problematic environment variables
    problematic_vars = clean_environment()
    if problematic_vars:
        logger.warning(f"Cleared problematic environment variables: {problematic_vars}")
    
    # Set environment variables for the Flask app
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["HOST"] = host
    env["DEBUG"] = "true" if debug else "false"
    
    if use_gunicorn and has_gunicorn():
        logger.info(f"Starting server with Gunicorn on {host}:{port} (debug={debug})")
        cmd = [
            "gunicorn", 
            "--bind", f"{host}:{port}", 
            "--access-logfile", "-", 
            "--error-logfile", "-",
            "--log-level", "info" if debug else "warning",
            "--timeout", "120",  # longer timeout for AI calculations
            "app:app"  # module:flask_app_variable
        ]
    else:
        logger.info(f"Starting server with Flask's built-in server on {host}:{port} (debug={debug})")
        if use_gunicorn:
            logger.warning("Gunicorn not found, falling back to Flask's built-in server")
        
        # Check for virtual environment
        if os.path.exists("venv") and os.path.isfile("venv/bin/python"):
            python_path = "venv/bin/python"
            logger.info("Using virtual environment Python")
        else:
            python_path = "python3"
            logger.info("Using system Python")
        
        cmd = [python_path, "app.py"]
    
    # Start the server process
    server_process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Log the process information
    logger.info(f"Server started with PID {server_process.pid}")
    
    # Start a thread to monitor the process output
    threading.Thread(target=monitor_output, daemon=True).start()
    
    # Wait for the server to start
    logger.info("Waiting for server to start...")
    for _ in range(10):
        time.sleep(1)
        if check_server_health(host, port):
            logger.info("Server is up and running!")
            return True
    
    logger.error("Server failed to start within the timeout period")
    return False


def monitor_output():
    """Monitor and log the output from the server process."""
    global server_process
    
    if not server_process:
        return
    
    for line in iter(server_process.stdout.readline, ""):
        line = line.strip()
        if line:
            logger.info(f"[SERVER] {line}")


def monitor_server(host, port, check_interval, max_restarts):
    """
    Monitor the server and restart it if it crashes or becomes unresponsive.
    
    Args:
        host: The host the server is running on
        port: The port the server is running on
        check_interval: How often to check the server health in seconds
        max_restarts: Maximum number of restart attempts
    """
    global server_process, restart_count, running
    
    logger.info(f"Starting server monitoring (interval={check_interval}s, max_restarts={max_restarts})")
    
    while running:
        # Check if the process is still running
        if server_process and server_process.poll() is not None:
            exit_code = server_process.poll()
            logger.warning(f"Server process has terminated (exit code: {exit_code})")
            server_process = None
        
        # If process is running, check if it's responding to HTTP requests
        if server_process:
            if not check_server_health(host, port):
                logger.warning("Server is not responding to HTTP requests")
                # Terminate the server process
                try:
                    logger.info("Terminating unresponsive server process")
                    server_process.terminate()
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Server process did not terminate gracefully, forcing")
                    server_process.kill()
                server_process = None
            else:
                logger.debug("Server health check passed")
        
        # If the server is not running, restart it
        if not server_process:
            if restart_count >= max_restarts:
                logger.error(f"Maximum restart attempts ({max_restarts}) reached. Exiting.")
                running = False
                break
            
            restart_count += 1
            logger.warning(f"Attempting to restart server (attempt {restart_count}/{max_restarts})")
            
            # Wait a bit before restarting
            time.sleep(1)
            
            if start_server(host, port, debug=False, use_gunicorn=True):
                logger.info("Server restarted successfully")
            else:
                logger.error("Failed to restart server")
        
        # Wait before the next check
        time.sleep(check_interval)


def signal_handler(sig, frame):
    """Handle termination signals to clean up the server process."""
    global running, server_process
    
    logger.info(f"Received signal {sig}, shutting down...")
    running = False
    
    if server_process:
        logger.info(f"Terminating server process (PID: {server_process.pid})")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            logger.info("Server process terminated gracefully")
        except subprocess.TimeoutExpired:
            logger.warning("Server process did not terminate gracefully, forcing")
            server_process.kill()
    
    logger.info("Shutdown complete")
    sys.exit(0)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Genetic Chess Engine server with persistence")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST,
                        help=f"Host to bind the server to (default: {DEFAULT_HOST})")
    parser.add_argument("--debug", action="store_true",
                        help="Run server in debug mode")
    parser.add_argument("--check-interval", type=int, default=DEFAULT_CHECK_INTERVAL,
                        help=f"Seconds between server health checks (default: {DEFAULT_CHECK_INTERVAL})")
    parser.add_argument("--max-restarts", type=int, default=DEFAULT_MAX_RESTARTS,
                        help=f"Maximum number of restart attempts (default: {DEFAULT_MAX_RESTARTS})")
    parser.add_argument("--no-gunicorn", action="store_true",
                        help="Don't use Gunicorn even if available")
    return parser.parse_args()


def main():
    """Main function to run the server with persistence."""
    args = parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting Persistent Server for Genetic Chess Engine")
    logger.info(f"Configuration: host={args.host}, port={args.port}, debug={args.debug}")
    
    # Start the server
    if start_server(args.host, args.port, args.debug, use_gunicorn=not args.no_gunicorn):
        # Start monitoring the server in a separate thread
        monitor_thread = threading.Thread(
            target=monitor_server,
            args=(args.host, args.port, args.check_interval, args.max_restarts),
            daemon=True
        )
        monitor_thread.start()
        
        # Keep the main thread alive
        try:
            while running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        logger.error("Failed to start the server")
        sys.exit(1)


if __name__ == "__main__":
    main() 