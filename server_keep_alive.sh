#!/bin/bash
# Wrapper script to ensure the Genetic Chess Engine stays running
# This script monitors the Flask server and restarts it if it crashes

# Default configuration
PORT=${PORT:-5001}
HOST=${HOST:-0.0.0.0}
DEBUG=${DEBUG:-false}
MAX_RESTARTS=10
CHECK_INTERVAL=5  # seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
restart_count=0
success_count=0

# Log file
log_file="server_keepalive.log"

# Function to log messages
log_message() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} - $1" | tee -a "$log_file"
}

# Function to check if server is running
check_server() {
    local url="http://127.0.0.1:${PORT}/"
    local response
    
    # Check if the server is responding to HTTP requests
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        return 0  # Server is running
    else
        return 1  # Server is not running
    fi
}

# Function to start the server
start_server() {
    log_message "${GREEN}Starting Genetic Chess Engine on ${HOST}:${PORT} (debug=${DEBUG})${NC}"
    
    # Completely clear problematic environment variables
    unset PYTHONHOME
    unset PYTHONPATH
    unset PYTHONSTARTUP
    unset PYTHONUSERBASE
    unset PYTHONEXECUTABLE
    
    # Check if virtual environment exists
    if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
        log_message "Using virtual environment"
        
        # Start the server in the background with a clean environment
        env -i \
            HOME="$HOME" \
            PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
            TERM="$TERM" \
            bash -c "cd \"$(pwd)\" && source venv/bin/activate && \
                     PORT=${PORT} HOST=${HOST} DEBUG=${DEBUG} \
                     python app.py" > server.log 2>&1 &
    else
        log_message "No virtual environment found, using system Python"
        
        # Start the server with system Python
        env -i \
            HOME="$HOME" \
            PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
            TERM="$TERM" \
            bash -c "cd \"$(pwd)\" && \
                     PORT=${PORT} HOST=${HOST} DEBUG=${DEBUG} \
                     python3 app.py" > server.log 2>&1 &
    fi
    
    # Store the PID of the server process
    server_pid=$!
    log_message "Server started with PID: ${server_pid}"
    
    # Wait for server to start
    local max_wait=15  # Maximum seconds to wait
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if check_server; then
            log_message "${GREEN}Server is running and responding on port ${PORT}${NC}"
            success_count=$((success_count + 1))
            return 0
        fi
        
        sleep 1
        waited=$((waited + 1))
        log_message "Waiting for server to start... ${waited}/${max_wait}"
    done
    
    log_message "${RED}Server did not start within ${max_wait} seconds${NC}"
    log_message "Last few lines of server.log:"
    tail -n 10 server.log | while read -r line; do
        log_message "  $line"
    done
    return 1
}

# Function to stop the server
stop_server() {
    if [ -n "$server_pid" ]; then
        log_message "${YELLOW}Stopping server with PID ${server_pid}${NC}"
        kill -15 "$server_pid" 2>/dev/null
        
        # Check if process was killed
        sleep 2
        if ! kill -0 "$server_pid" 2>/dev/null; then
            log_message "Server stopped successfully"
        else
            # If not killed with SIGTERM, try SIGKILL
            log_message "${RED}Server did not stop gracefully, using SIGKILL${NC}"
            kill -9 "$server_pid" 2>/dev/null
        fi
    else
        log_message "${YELLOW}No server PID found to stop${NC}"
        
        # Try to find and kill Python processes running app.py
        pkill -f "python.*app.py" 2>/dev/null
    fi
    
    # Make sure no zombie processes are left
    log_message "Ensuring no lingering Python processes for app.py"
    pkill -f "python.*app.py" 2>/dev/null || true
}

# Function to check server and restart if needed
monitor_and_restart() {
    log_message "${BLUE}Monitoring server on port ${PORT}...${NC}"
    
    while true; do
        if ! check_server; then
            log_message "${RED}Server is not responding${NC}"
            
            # Check if restart limit has been reached
            if [ $restart_count -ge $MAX_RESTARTS ]; then
                log_message "${RED}Maximum restart attempts (${MAX_RESTARTS}) reached. Giving up.${NC}"
                return 1
            fi
            
            # Stop the server (if it's still running but not responding)
            stop_server
            
            # Restart the server
            restart_count=$((restart_count + 1))
            log_message "${YELLOW}Restarting server (attempt ${restart_count}/${MAX_RESTARTS})${NC}"
            
            if start_server; then
                log_message "${GREEN}Server restarted successfully${NC}"
            else
                log_message "${RED}Failed to restart server${NC}"
                sleep $CHECK_INTERVAL
                continue
            fi
        else
            # Server is running correctly
            if [ $((restart_count + success_count)) -eq 1 ]; then
                log_message "${GREEN}Server is running correctly${NC}"
            fi
        fi
        
        # Wait before checking again
        sleep $CHECK_INTERVAL
    done
}

# Main function
main() {
    log_message "${BLUE}Starting Genetic Chess Engine keep-alive script${NC}"
    log_message "Configuration: PORT=${PORT}, HOST=${HOST}, DEBUG=${DEBUG}"
    
    # Initialize log file
    echo "=== Genetic Chess Engine Keep-Alive Log $(date) ===" > "$log_file"
    
    # Make sure no existing server is running
    log_message "Checking for existing server processes"
    pkill -f "python.*app.py" 2>/dev/null || true
    
    # Trap Ctrl+C and other signals
    trap cleanup INT TERM
    
    # Initial server start
    if start_server; then
        log_message "${GREEN}Server started successfully${NC}"
    else
        log_message "${RED}Failed to start server${NC}"
        return 1
    fi
    
    # Start monitoring and restart cycle
    monitor_and_restart
}

# Cleanup function for when the script is terminated
cleanup() {
    log_message "${YELLOW}Keep-alive script is shutting down...${NC}"
    stop_server
    log_message "Server summary: ${success_count} successful starts, ${restart_count} restarts"
    log_message "${BLUE}Exiting. Log file: ${log_file}${NC}"
    exit 0
}

# Run the main function
main 