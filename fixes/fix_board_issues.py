#!/usr/bin/env python
import json
from flask import Flask
from app import app, current_position, board_to_dict, square_to_coord, coord_to_square
from chess_logic_by_thomasahle import Position, initial

def check_board_representation():
    """Check the board representation for issues and print detailed information"""
    print("\n=== BOARD REPRESENTATION CHECK ===")
    
    # First, check the initial variable
    print("\nInitial board string:")
    print(initial)
    
    # Create a new position with the initial board
    pos = Position(initial, 0, (True,True), (True,True), 0, 0)
    
    print("\nPosition board string:")
    print(pos.board)
    
    # Get the board dictionary
    board = board_to_dict(pos)
    
    print("\nBoard dictionary (should have 32 pieces):")
    print(f"Total pieces: {len(board)}")
    
    # Check how many black pieces are in the board dictionary
    black_pieces = [p for p in board.values() if p.get('color') == 'black']
    print(f"Black pieces: {len(black_pieces)}")
    white_pieces = [p for p in board.values() if p.get('color') == 'white']
    print(f"White pieces: {len(white_pieces)}")
    
    # Check for the word 'black' in the serialized board
    board_json = json.dumps(board)
    black_count = board_json.count('"color": "black"')
    total_black_count = board_json.count('black')
    
    print("\nInstances of 'black' in the board JSON:")
    print(f"Expected instances (as color property): {len(black_pieces)}")
    print(f"Actual instances (total): {total_black_count}")
    
    # Test a move to see if piece movement is working
    print("\n=== PIECE MOVEMENT CHECK ===")
    e2 = square_to_coord('e2')
    e4 = square_to_coord('e4')
    player_move = (e2, e4)
    
    print(f"Move: e2 ({e2}) to e4 ({e4})")
    
    # Check if the move is valid
    valid_moves = list(pos.gen_moves())
    if player_move in valid_moves:
        print("Move is VALID")
        # Try making the move
        new_pos = pos.move(player_move)
        new_board = board_to_dict(new_pos)
        
        # Check if the pawn moved
        if 'e4' in new_board and 'e2' not in new_board:
            print("Pawn successfully moved from e2 to e4!")
        else:
            print("ERROR: Pawn did not move correctly!")
            print("Squares in new board:", new_board.keys())
    else:
        print("Move is INVALID")
        print(f"Valid moves (showing first 5): {[(coord_to_square(m[0]), coord_to_square(m[1])) for m in valid_moves[:5] if m[0] < 120 and m[1] < 120]}...")
    
    return board, valid_moves

def test_api_calls():
    """Test API calls to see if the backend is correctly handling requests"""
    print("\n=== API CALLS TEST ===")
    
    # Create a test client
    client = app.test_client()
    
    # Initialize a game
    print("\nTesting /initialize endpoint:")
    response = client.post('/initialize',
                          data=json.dumps({'difficulty': 'easy'}),
                          content_type='application/json')
    
    data = json.loads(response.data)
    print(f"Response status: {response.status_code}")
    print(f"Game state: {data.get('gameState')}")
    print(f"Board size: {len(data.get('board', {}))}")
    
    # Try making a move
    print("\nTesting /move endpoint:")
    response = client.post('/move',
                          data=json.dumps({'from': 'e2', 'to': 'e4'}),
                          content_type='application/json')
    
    data = json.loads(response.data)
    print(f"Response status: {response.status_code}")
    print(f"Move valid: {data.get('valid')}")
    if not data.get('valid'):
        print(f"Error message: {data.get('message')}")
    else:
        print(f"AI move: {data.get('aiMove')}")
        print(f"New board size: {len(data.get('board', {}))}")
    
    return data

if __name__ == "__main__":
    # Run the tests
    board, valid_moves = check_board_representation()
    api_data = test_api_calls()
    
    # Print recommendations based on findings
    print("\n=== RECOMMENDATIONS ===")
    
    # Issue 1: Black word all over the board
    if board and len([p for p in board.values() if p.get('color') == 'black']) == 0:
        print("Issue: No black pieces found in the board dictionary.")
        print("Fix: Check the board_to_dict function to ensure it's correctly identifying black pieces.")
    
    # Issue 2: Pieces not moving
    if not any((square_to_coord('e2'), square_to_coord('e4')) in m for m in valid_moves):
        print("Issue: The e2-e4 pawn move is not recognized as valid.")
        print("Fix: Check the coordinate conversion functions (square_to_coord, coord_to_square) and ensure they match the chess engine's expectations.")
    
    # Issue 3: Pieces in wrong position
    if board and len(board) < 32:
        print("Issue: Not all chess pieces are being displayed on the board.")
        print("Fix: Check the board_to_dict function to ensure it's correctly parsing all pieces from the board representation.") 