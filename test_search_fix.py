#!/usr/bin/env python3
"""
Simple test script to verify that the search method in Minimax returns a valid move tuple.
This script doesn't rely on Flask or the complete app to make testing easier.
"""

from chess_logic_by_thomasahle import Position, initial
from minimax import Minimax
from genetic_programming import makerandomtree

def test_search_method():
    # Initialize the chess position
    position = Position(initial, 0, (True, True), (True, True), 0, 0)
    print("Initial position created")
    
    # Create a heuristic for the AI
    heuristic = makerandomtree(3, position)
    print("Heuristic created")
    
    # Initialize the searcher
    searcher = Minimax(heuristic)
    print("Searcher initialized")
    
    # Get all legal moves for the starting position
    valid_moves = list(position.gen_moves())
    print(f"Found {len(valid_moves)} valid moves from the initial position")
    
    # Choose a sample player move (e.g., e2 to e4)
    sample_move = valid_moves[0]
    print(f"Using sample move: {sample_move}")
    
    # Execute the player's move
    new_position = position.move(sample_move)
    print("Applied player's move")
    
    # Try to get a move from the AI
    print("Calling search method...")
    ai_move_result = searcher.search(new_position, secs=1.5)
    print(f"Search result: {ai_move_result}")
    
    # The search result should be a tuple (move, score)
    if isinstance(ai_move_result, tuple) and len(ai_move_result) == 2:
        ai_move, ai_score = ai_move_result
        print(f"✓ AI move result is a tuple (move, score): {ai_move}, {ai_score}")
    else:
        print(f"✗ AI move result is not a tuple (move, score): {ai_move_result}")
        return False
    
    # Check that the AI move is a tuple of two integers (from_coord, to_coord)
    if isinstance(ai_move, tuple) and len(ai_move) == 2:
        print(f"✓ AI move is a tuple of length 2: {ai_move}")
    else:
        print(f"✗ AI move is not a tuple of length 2: {ai_move}")
        return False
    
    # Generate all valid moves for the AI's position
    valid_ai_moves = list(new_position.gen_moves())
    
    # Check that the AI's move is in the list of valid moves
    if ai_move in valid_ai_moves:
        print(f"✓ AI move {ai_move} is in the list of valid moves")
    else:
        print(f"✗ AI move {ai_move} is not in the list of valid moves")
        return False
    
    print("All tests passed! The search method now correctly returns a (move, score) tuple.")
    return True

if __name__ == "__main__":
    print("Testing search method fix...")
    success = test_search_method()
    if success:
        print("\nSUCCESS: The search method in Minimax now correctly returns a (move, score) tuple.")
    else:
        print("\nFAILURE: The search method in Minimax is still not returning a (move, score) tuple correctly.") 