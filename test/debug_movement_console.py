#!/usr/bin/env python3
import sys
import os
import json
import time
import requests
from pprint import pprint

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define the API endpoints
API_BASE = "http://localhost:5001"
INITIALIZE_ENDPOINT = f"{API_BASE}/initialize"
MOVE_ENDPOINT = f"{API_BASE}/move"

def print_board(board):
    """Print the board in a user-friendly format"""
    print("\nBoard state:")
    ranks = "87654321"
    files = "abcdefgh"
    
    # Print file labels
    print("  ", end="")
    for file in files:
        print(f" {file} ", end="")
    print()
    
    # Print the board with rank labels
    for rank in ranks:
        print(f"{rank} ", end="")
        for file in files:
            square = f"{file}{rank}"
            if square in board:
                piece = board[square]
                piece_symbol = piece['code']
                print(f" {piece_symbol} ", end="")
            else:
                print(" . ", end="")
        print(f" {rank}")
    
    # Print file labels again
    print("  ", end="")
    for file in files:
        print(f" {file} ", end="")
    print("\n")

def print_legal_moves(moves):
    """Print the legal moves in a user-friendly format"""
    print("\nLegal moves:")
    for move in moves:
        print(f"  {move['from']} -> {move['to']}")
    print()

def initialize_game():
    """Initialize a new game and return the initial state"""
    try:
        response = requests.post(
            INITIALIZE_ENDPOINT,
            json={"difficulty": "easy"},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        print("Game initialized successfully!")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error initializing game: {e}")
        sys.exit(1)

def make_move(from_square, to_square):
    """Make a move and return the new state"""
    try:
        print(f"Attempting move from {from_square} to {to_square}...")
        response = requests.post(
            MOVE_ENDPOINT,
            json={"from": from_square, "to": to_square},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('valid', False):
            print(f"Move from {from_square} to {to_square} was successful!")
            if data.get('aiMove'):
                ai_from = data['aiMove']['from']
                ai_to = data['aiMove']['to']
                print(f"AI responded with move from {ai_from} to {ai_to}")
        else:
            print(f"Move was rejected: {data.get('message', 'Unknown error')}")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error making move: {e}")
        sys.exit(1)

def main():
    print("====== Chess Movement Debug Console ======")
    print(f"Connecting to API at {API_BASE}")
    
    # Check if the API is accessible
    try:
        requests.get(API_BASE)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to the API at {API_BASE}")
        print("Make sure the Flask application is running on port 5001")
        print("Run: PORT=5001 ./run.sh")
        sys.exit(1)
    
    # Initialize a new game
    game_data = initialize_game()
    board = game_data.get('board', {})
    print_board(board)
    
    # Test some specific moves
    test_moves = [
        ("e2", "e4"),  # Common opening pawn move
        ("d2", "d4"),  # Another common pawn move
        ("g1", "f3"),  # Knight move
    ]
    
    for from_square, to_square in test_moves:
        move_data = make_move(from_square, to_square)
        
        # Display the updated board and legal moves
        if 'board' in move_data:
            print_board(move_data['board'])
        
        if 'legalMoves' in move_data:
            print_legal_moves(move_data['legalMoves'])
        
        # Pause between moves to see the output
        time.sleep(1)
    
    print("====== Debug session complete ======")

if __name__ == "__main__":
    main() 