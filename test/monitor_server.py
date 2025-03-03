#!/usr/bin/env python3
import sys
import os
import time
import json
import signal
import requests
from datetime import datetime
import argparse

# Constants
DEFAULT_PORT = 5001
DEFAULT_HOST = "127.0.0.1"
CHECK_INTERVAL = 10  # seconds
LOG_FILE = "server_monitor.log"

class ServerMonitor:
    """Class to monitor an existing server"""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, log_file=LOG_FILE):
        self.host = host
        self.port = port
        self.server_url = f"http://{host}:{port}"
        self.log_file = log_file
        self.running = False
        self.start_time = None
        self.check_count = 0
        self.success_count = 0
        self.failure_count = 0
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle termination signals"""
        print(f"\nReceived signal {sig}, shutting down...")
        self.log_message(f"Monitor shutting down due to signal {sig}")
        self.print_summary()
        sys.exit(0)
    
    def log_message(self, message):
        """Log a message to the log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} - {message}\n")
    
    def print_summary(self):
        """Print a summary of the monitoring session"""
        if self.start_time:
            duration = int(time.time() - self.start_time)
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            duration_str = "00:00:00"
        
        print("\nMonitoring Summary:")
        print(f"Duration: {duration_str}")
        print(f"Total checks: {self.check_count}")
        print(f"Successful checks: {self.success_count}")
        print(f"Failed checks: {self.failure_count}")
        
        if self.check_count > 0:
            success_rate = (self.success_count / self.check_count) * 100
            print(f"Success rate: {success_rate:.2f}%")
        
        print(f"Log file: {os.path.abspath(self.log_file)}")
    
    def check_server(self):
        """Check if the server is responding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.check_count += 1
        
        try:
            # Try to access the root page
            response = requests.get(f"{self.server_url}/", timeout=5)
            
            if response.status_code == 200:
                self.success_count += 1
                status_msg = f"{timestamp} - Server is responding (Status: {response.status_code})"
                print(status_msg)
                self.log_message(status_msg)
                return True
            else:
                self.failure_count += 1
                status_msg = f"{timestamp} - Server returned status code {response.status_code}"
                print(status_msg)
                self.log_message(status_msg)
                return False
                
        except requests.exceptions.ConnectionError:
            self.failure_count += 1
            status_msg = f"{timestamp} - CONNECTION ERROR: Failed to connect to server"
            print(status_msg)
            self.log_message(status_msg)
            return False
        except requests.exceptions.Timeout:
            self.failure_count += 1
            status_msg = f"{timestamp} - TIMEOUT: Server did not respond within timeout period"
            print(status_msg)
            self.log_message(status_msg)
            return False
        except Exception as e:
            self.failure_count += 1
            status_msg = f"{timestamp} - ERROR: {str(e)}"
            print(status_msg)
            self.log_message(status_msg)
            return False
    
    def test_api_endpoint(self, endpoint, method="GET", data=None):
        """Test a specific API endpoint"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        try:
            if method.upper() == "POST":
                response = requests.post(
                    f"{self.server_url}/{endpoint}", 
                    json=data or {}, 
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            else:
                response = requests.get(f"{self.server_url}/{endpoint}", timeout=5)
            
            if response.status_code == 200:
                status_msg = f"{timestamp} - Endpoint '{endpoint}' is responding"
                print(status_msg)
                self.log_message(status_msg)
                return response.json()
            else:
                status_msg = f"{timestamp} - Endpoint '{endpoint}' returned status code {response.status_code}"
                print(status_msg)
                self.log_message(status_msg)
                return None
                
        except Exception as e:
            status_msg = f"{timestamp} - Error testing endpoint '{endpoint}': {str(e)}"
            print(status_msg)
            self.log_message(status_msg)
            return None
    
    def run_comprehensive_check(self):
        """Run a comprehensive check of the server's API endpoints"""
        print("\nRunning comprehensive API check...")
        
        # Check main page
        self.check_server()
        
        # Test initialize endpoint
        initialize_data = self.test_api_endpoint("initialize", method="POST", data={"difficulty": "easy"})
        
        if initialize_data:
            # Test move endpoint
            move_data = self.test_api_endpoint("move", method="POST", data={"from": "e2", "to": "e4"})
            
            if move_data and move_data.get("valid"):
                print("API check successful: Move was valid")
                self.log_message("API check successful: Move was valid")
            else:
                print("API check failed: Move was not valid")
                self.log_message("API check failed: Move was not valid")
        else:
            print("API check failed: Could not initialize game")
            self.log_message("API check failed: Could not initialize game")
    
    def start_monitoring(self, duration=None, comprehensive_interval=10):
        """Start monitoring the server"""
        print(f"Starting to monitor server at {self.server_url}")
        print(f"Logging to {os.path.abspath(self.log_file)}")
        print(f"Press Ctrl+C to stop monitoring")
        
        self.log_message(f"=== Monitoring started for server at {self.server_url} ===")
        
        self.running = True
        self.start_time = time.time()
        comprehensive_counter = 0
        
        while self.running:
            # Check if we need to run a comprehensive check
            if comprehensive_counter == 0:
                self.run_comprehensive_check()
            else:
                self.check_server()
            
            # Increment the comprehensive counter and reset if needed
            comprehensive_counter = (comprehensive_counter + 1) % comprehensive_interval
            
            # Check if we've reached the duration limit
            if duration and (time.time() - self.start_time) >= duration:
                print(f"\nReached specified duration of {duration} seconds")
                self.log_message(f"Monitoring stopped after reaching duration of {duration} seconds")
                self.running = False
                break
            
            # Wait before the next check
            time.sleep(CHECK_INTERVAL)
        
        self.print_summary()

def main():
    """Main function to run the server monitor"""
    parser = argparse.ArgumentParser(description='Monitor a Flask server for stability.')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Server host (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Server port (default: {DEFAULT_PORT})')
    parser.add_argument('--interval', type=int, default=CHECK_INTERVAL, 
                        help=f'Check interval in seconds (default: {CHECK_INTERVAL})')
    parser.add_argument('--log', default=LOG_FILE, help=f'Log file (default: {LOG_FILE})')
    parser.add_argument('--duration', type=int, default=None, 
                        help='Duration to monitor in seconds (default: indefinite)')
    
    args = parser.parse_args()
    
    global CHECK_INTERVAL
    CHECK_INTERVAL = args.interval
    
    monitor = ServerMonitor(host=args.host, port=args.port, log_file=args.log)
    monitor.start_monitoring(duration=args.duration)

if __name__ == "__main__":
    main() 