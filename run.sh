#!/bin/bash
# Wrapper script to start the Genetic Chess Engine application
# This script ensures that Cursor's Python environment variables don't interfere with the application

# Unset problematic environment variables
unset PYTHONHOME
unset PYTHONPATH

echo "Starting Genetic Chess Engine with clean Python environment..."

# Check if we have a virtual environment
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo "Using virtual environment..."
    source venv/bin/activate
    python app.py
else
    echo "No virtual environment found, using system Python..."
    python3 app.py
fi

# If we get here, the application has stopped
echo "Application has stopped." 