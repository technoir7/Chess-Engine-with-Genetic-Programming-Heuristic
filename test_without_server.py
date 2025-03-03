#!/usr/bin/env python3
"""
Test script that directly tests the app functionality without running a server.
This script initializes the app as a test client and directly tests the piece movement.
"""

import sys
import json
from app import app, square_to_coord, coord_to_square

def test_coordinate_functions():
    print("\n--- Testing Coordinate Functions ---")
    
    # Test key coordinate transformations
    test_squares = [
        ('a1', 91),  # A1 = 91
        ('h1', 98),  # H1 = 98
        ('a8', 21),  # A8 = 21
        ('h8', 28),  # H8 = 28
        ('e2', 85),  # e2 should be 85
        ('e4', 65),  # e4 should be 65
    ]
    
    # Test square_to_coord
    for square, expected in test_squares:
        try:
            result = square_to_coord(square)
            if result == expected:
                print(f"✓ square_to_coord('{square}') = {result}")
            else:
                print(f"✗ square_to_coord('{square}') = {result}, expected {expected}")
        except Exception as e:
            print(f"✗ Error with square_to_coord('{square}'): {e}")
    
    # Test coord_to_square
    for square, coord in test_squares:
        try:
            result = coord_to_square(coord)
            if result == square:
                print(f"✓ coord_to_square({coord}) = '{result}'")
            else:
                print(f"✗ coord_to_square({coord}) = '{result}', expected '{square}'")
        except Exception as e:
            print(f"✗ Error with coord_to_square({coord}): {e}")
    
    print("--- Coordinate Functions Test Complete ---\n")

def test_piece_movement():
    print("\n--- Testing Piece Movement ---")
    
    # Create a test client
    with app.test_client() as client:
        # Initialize the game
        init_response = client.post('/initialize',
                                 data=json.dumps({"difficulty": "easy"}),
                                 content_type='application/json')
        init_data = init_response.get_json()
        
        print(f"Game initialized, got response: {init_response.status_code}")
        if init_response.status_code != 200:
            print(f"Error initializing game: {init_data}")
            return
        
        # Get the initial board
        initial_board = init_data.get('board', {})
        print(f"Initial board has {len(initial_board)} pieces")
        
        # Check that e2 has a white pawn
        if 'e2' in initial_board:
            piece = initial_board['e2']
            print(f"Piece at e2: {piece}")
        else:
            print("❌ No piece at e2")
        
        # Try to move the pawn from e2 to e4
        print("\nAttempting to move e2 to e4...")
        move_response = client.post('/move',
                                 data=json.dumps({"from": "e2", "to": "e4"}),
                                 content_type='application/json')
        move_data = move_response.get_json()
        
        print(f"Move response status: {move_response.status_code}")
        
        # Check if there was an error
        if 'error' in move_data:
            print(f"❌ Move error: {move_data['error']}")
        else:
            # Check if the move was valid
            if move_data.get('valid', False):
                print("✓ Move was valid!")
                
                # Check the updated board
                board = move_data.get('board', {})
                
                # Verify e4 now has a piece
                if 'e4' in board:
                    piece = board['e4']
                    print(f"Piece at e4: {piece}")
                else:
                    print("❌ No piece at e4 after move")
                
                # Verify e2 is now empty
                if 'e2' not in board:
                    print("✓ e2 is now empty")
                else:
                    print("❌ e2 still has a piece: {board['e2']}")
                
                # Check for AI move
                if 'aiMove' in move_data:
                    ai_move = move_data['aiMove']
                    print(f"AI moved from {ai_move.get('from')} to {ai_move.get('to')}")
                else:
                    print("❌ No AI move found in response")
                
            else:
                print("❌ Move was invalid according to server")
        
        print("--- Piece Movement Test Complete ---\n")

def main():
    print("=== Running Test Suite without Server ===")
    
    # Run tests
    test_coordinate_functions()
    test_piece_movement()
    
    print("=== Test Suite Complete ===")

if __name__ == "__main__":
    main() 