#!/bin/bash
# Wrapper script to start the persistent server with a clean environment

# Unset problematic environment variables
unset PYTHONHOME
unset PYTHONPATH
unset PYTHONSTARTUP
unset PYTHONUSERBASE
unset PYTHONEXECUTABLE

echo "Starting Genetic Chess Engine Persistent Server..."

# Check if we have a virtual environment
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo "Using virtual environment..."
    source venv/bin/activate
    ./run_persistent_server.py "$@"
else
    echo "No virtual environment found, using system Python..."
    python3 ./run_persistent_server.py "$@"
fi

# If we get here, the persistent server has stopped
echo "Persistent server has stopped." 