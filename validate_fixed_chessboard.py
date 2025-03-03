#!/usr/bin/env python3
"""
Simple standalone script to validate our chessboard fixes.
This script doesn't depend on unittest so it should run directly with Python.
"""

from chess_logic_by_thomasahle import Position, initial
from app import board_to_dict, _generate_standard_initial_board

def test_standard_initial_board():
    """Test that the standard initial board has all 32 pieces."""
    standard_board = _generate_standard_initial_board()
    piece_count = len(standard_board)
    
    print(f"Standard initial board has {piece_count} pieces (expected 32)")
    
    if piece_count != 32:
        print("ERROR: Standard initial board doesn't have 32 pieces!")
        return False
    
    # Check for specific pieces that were missing
    critical_squares = ['h8', 'h7']  # Black rook and pawn that were missing
    
    for square in critical_squares:
        if square not in standard_board:
            print(f"ERROR: {square} is missing from standard initial board!")
            return False
        
        piece = standard_board[square]
        print(f"Found piece at {square}: {piece['color']} {piece['type']}")
    
    # Check for white pieces
    white_squares = [f"{f}{r}" for f in "abcdefgh" for r in "12"]
    for square in white_squares:
        if square not in standard_board:
            print(f"ERROR: White piece at {square} is missing!")
            return False
        
        piece = standard_board[square]
        if piece['color'] != 'white':
            print(f"ERROR: Piece at {square} should be white but is {piece['color']}!")
            return False
    
    print("All white pieces are present and correctly colored")
    return True

def test_position_to_dict():
    """Test that converting from a Position to a dictionary works properly."""
    position = Position(initial, 0, (True, True), (True, True), 0, 0)
    board_dict = board_to_dict(position)
    
    piece_count = len(board_dict)
    print(f"Converted board has {piece_count} pieces (expected 32)")
    
    if piece_count != 32:
        print("ERROR: Converted board doesn't have 32 pieces!")
        return False
    
    # Check for specific pieces that were missing
    critical_squares = ['h8', 'h7']  # Black rook and pawn that were missing
    
    for square in critical_squares:
        if square not in board_dict:
            print(f"ERROR: {square} is missing from converted board!")
            return False
        
        piece = board_dict[square]
        print(f"Found piece at {square}: {piece['color']} {piece['type']}")
    
    # Check for white pieces
    white_squares = [f"{f}{r}" for f in "abcdefgh" for r in "12"]
    for square in white_squares:
        if square not in board_dict:
            print(f"ERROR: White piece at {square} is missing!")
            return False
        
        piece = board_dict[square]
        if piece['color'] != 'white':
            print(f"ERROR: Piece at {square} should be white but is {piece['color']}!")
            return False
    
    print("All white pieces are present and correctly colored in the converted board")
    return True

def main():
    """Run the tests."""
    print("Validating chessboard fixes...")
    print("\n--- Testing Standard Initial Board ---")
    standard_board_passed = test_standard_initial_board()
    
    print("\n--- Testing Position to Dict Conversion ---")
    position_to_dict_passed = test_position_to_dict()
    
    print("\n--- Summary ---")
    if standard_board_passed and position_to_dict_passed:
        print("SUCCESS: All chessboard fixes validated!")
        return 0
    else:
        print("FAILURE: Some tests failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 