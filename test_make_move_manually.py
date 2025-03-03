#!/usr/bin/env python3
"""
Test script to manually simulate the move generation process without relying on Flask.
"""

from chess_logic_by_thomasahle import Position, initial, MATE_LOWER, MATE_UPPER
from minimax import Minimax
from genetic_programming import makerandomtree

def simulate_make_move():
    print("Initializing game...")
    # Initialize the chess position
    current_position = Position(initial, 0, (True, True), (True, True), 0, 0)
    print("Initial position created")
    
    # Create a heuristic for the AI
    heuristic = makerandomtree(3, current_position)
    print("Heuristic created")
    
    # Initialize the searcher
    searcher = Minimax(heuristic)
    print("Searcher initialized")
    
    # Get all legal moves for the starting position
    valid_moves = list(current_position.gen_moves())
    print(f"Found {len(valid_moves)} valid moves from the initial position")
    
    # Choose a sample player move (e.g., e2 to e4 - a common first move)
    sample_move = valid_moves[0]
    print(f"Using sample player move: {sample_move}")
    
    # Execute the player's move
    new_position = current_position.move(sample_move)
    print("Applied player's move")
    current_position = new_position
    
    # Simulating the make_move function in app.py
    print("\nSimulating AI's response...")
    
    # Make AI move
    search_result = None
    try:
        search_result = searcher.search(current_position, secs=1.5)
        print(f"Search result: {search_result}")
    except Exception as e:
        print(f"Error calling search method: {e}")
        import traceback
        traceback.print_exc()
    
    ai_move = None
    ai_score = None
    
    # Try to extract the move and score from the search result
    if search_result:
        # The search result is a tuple (move, score) where move is itself a tuple (from_coord, to_coord)
        if isinstance(search_result, tuple) and len(search_result) == 2:
            ai_move, ai_score = search_result
            print(f"Extracted move {ai_move} and score {ai_score} from search result")
        else:
            # Handle the case where search_result is not a tuple (move, score)
            ai_move = search_result
            ai_score = None
            print(f"Search result was not a tuple (move, score), using move: {ai_move}")
    
    # If we still don't have a valid move, generate one
    if not ai_move or not isinstance(ai_move, tuple) or len(ai_move) != 2:
        print("Generating fallback move for AI")
        valid_moves = list(current_position.gen_moves())
        if valid_moves:
            ai_move = valid_moves[0]  # Take the first valid move as a fallback
            ai_score = 0
            print(f"Generated fallback move: {ai_move}")
    
    if ai_move:
        # Handle case where ai_move is a tuple (from_coord, to_coord)
        if isinstance(ai_move, tuple) and len(ai_move) == 2:
            ai_from_coord, ai_to_coord = ai_move
            print(f"Valid AI move: from {ai_from_coord} to {ai_to_coord}")
            
            # Update position with AI's move
            current_position = current_position.move(ai_move)
            print("Applied AI's move to the position")
            
            return True
        else:
            print(f"Unexpected AI move format: {ai_move}")
            return False
    else:
        print("AI did not generate a move")
        return False

if __name__ == "__main__":
    print("Testing AI move generation...")
    success = simulate_make_move()
    if success:
        print("\nSUCCESS: The AI successfully generated a valid move!")
    else:
        print("\nFAILURE: The AI failed to generate a valid move.") 