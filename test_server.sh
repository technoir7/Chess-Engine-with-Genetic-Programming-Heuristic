#!/bin/bash
# Script to test the server with a clean environment

# Clear problematic environment variables
unset PYTHONHOME
unset PYTHONPATH
unset PYTHONSTARTUP
unset PYTHONUSERBASE
unset PYTHONEXECUTABLE

# Change to the project root directory
cd "$(dirname "$0")"

echo "=== Testing Genetic Chess Engine Server ==="
echo "Checking if server is running..."

# Check if server is running
if curl -s http://localhost:5001/ > /dev/null; then
    echo "Server is running. Proceeding with tests..."
else
    echo "Server is not running. Attempting to start it..."
    
    # Check if the server_keep_alive.sh script exists
    if [ -f "./server_keep_alive.sh" ]; then
        echo "Starting server using server_keep_alive.sh..."
        # Start the server in the background
        nohup ./server_keep_alive.sh > server_startup.log 2>&1 &
        
        # Wait for the server to start
        for i in {1..10}; do
            echo "Waiting for server to start ($i/10)..."
            sleep 2
            if curl -s http://localhost:5001/ > /dev/null; then
                echo "Server started successfully!"
                break
            fi
            if [ $i -eq 10 ]; then
                echo "Failed to start server after 10 attempts."
                echo "Please check server_startup.log for details."
                exit 1
            fi
        done
    else
        echo "Error: server_keep_alive.sh not found."
        echo "Please start the server manually using one of:"
        echo "  1. ./run.sh"
        echo "  2. ./server_keep_alive.sh"
        echo "  3. ./run_stable_server.py"
        exit 1
    fi
fi

# Check if virtual environment exists
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo "Using virtual environment..."
    # Run the test with venv python
    source venv/bin/activate
    python test/test_server_alive.py
else
    echo "No virtual environment found, using system Python..."
    python3 test/test_server_alive.py
fi 