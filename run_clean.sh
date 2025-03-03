#!/bin/bash
# This script runs the app with a clean environment to avoid Cursor's Python environment issues

# Unset PYTHONHOME and PYTHONPATH which may be causing issues
unset PYTHONHOME
unset PYTHONPATH

# Kill any existing Flask processes
pkill -f "python.*app.py" || true

# Define colors for better visibility
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting the chess application...${NC}"

# Run with the system Python and capture output to log file
/usr/bin/python3 app.py > app_output.log 2>&1 &
APP_PID=$!

# Wait a moment for the app to start
sleep 2

# Check if the app is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ | grep -q "200"; then
    echo -e "${GREEN}App started successfully on http://localhost:5000/${NC}"
    echo -e "Log file: app_output.log"
    
    # Now run the test for missing pieces
    echo -e "\n${YELLOW}Running test for missing pieces...${NC}"
    
    # Capture the test output
    TEST_OUTPUT=$(/usr/bin/python3 -c "
import unittest
import json
import sys
import requests

# Check if h8 and h7 are present in the board
response = requests.post('http://localhost:5000/initialize', 
                        json={'difficulty': 'medium'})

if response.status_code != 200:
    print('Error: Failed to initialize the board')
    sys.exit(1)

data = response.json()
board = data['board']

# Check total piece count
total_pieces = len(board)
if total_pieces != 32:
    print(f'Error: Expected 32 pieces but found {total_pieces}')
    sys.exit(1)

# Check for h8 rook
if 'h8' not in board:
    print('Error: Black rook at h8 is missing')
    sys.exit(1)
elif board['h8']['type'] != 'r' or board['h8']['color'] != 'black':
    print(f'Error: h8 should have a black rook, but found {board[\"h8\"]}')
    sys.exit(1)

# Check for h7 pawn
if 'h7' not in board:
    print('Error: Black pawn at h7 is missing')
    sys.exit(1)
elif board['h7']['type'] != 'p' or board['h7']['color'] != 'black':
    print(f'Error: h7 should have a black pawn, but found {board[\"h7\"]}')
    sys.exit(1)

# Check for white pieces
white_squares = [f'{f}{r}' for f in 'abcdefgh' for r in '12']
for square in white_squares:
    if square not in board:
        print(f'Error: White piece at {square} is missing')
        sys.exit(1)
    if board[square]['color'] != 'white':
        print(f'Error: Piece at {square} should be white but is {board[square][\"color\"]}')
        sys.exit(1)

print('Success! All pieces are present!')
")
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}$TEST_OUTPUT${NC}"
    else
        echo -e "${RED}$TEST_OUTPUT${NC}"
    fi
    
    echo -e "\n${GREEN}Chess app is running!${NC}"
    echo -e "To stop the app, run: kill $APP_PID"
else
    echo -e "${RED}Failed to start app, check app_output.log for errors${NC}"
    cat app_output.log
    exit 1
fi 