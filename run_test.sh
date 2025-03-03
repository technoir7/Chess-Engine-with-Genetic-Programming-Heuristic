#!/bin/bash
# Simple wrapper to run tests with a clean Python environment

# Clear problematic environment variables
unset PYTHONHOME
unset PYTHONPATH
unset PYTHONSTARTUP
unset PYTHONUSERBASE
unset PYTHONEXECUTABLE

# Check if virtual environment exists
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo "Using virtual environment..."
    # Activate venv and run the test
    source venv/bin/activate
    python "$@"
else
    echo "No virtual environment found, using system Python..."
    python3 "$@"
fi 