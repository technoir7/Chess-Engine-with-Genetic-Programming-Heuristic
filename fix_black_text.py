#!/usr/bin/env python
import json
from flask import Flask
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

def test_board_serialization():
    """Test the board serialization to check for the 'black' text issue"""
    # Create a test client
    client = app.test_client()
    
    # Initialize a game
    response = client.post('/initialize',
                          data=json.dumps({'difficulty': 'medium'}),
                          content_type='application/json')
    
    # Check the response
    data = json.loads(response.data)
    board_dict = data.get('board', {})
    
    # Print the entire board dictionary
    print("\nBoard Dictionary:")
    print(json.dumps(board_dict, indent=2))
    
    # Print a sample of a black piece
    black_pieces = [(square, piece) for square, piece in board_dict.items() 
                    if piece.get('color') == 'black']
    if black_pieces:
        print(f"\nFound {len(black_pieces)} black pieces")
        print(f"Sample black piece: {black_pieces[0]}")
    else:
        print("\nNo black pieces found!")
        
        # Check the raw response
        print("\nRaw response (first 500 chars):")
        print(response.data[:500])
        
        # Check if black pieces exist in the board representation
        position = Position(initial, 0, (True,True), (True,True), 0, 0)
        internal_board = board_to_dict(position)
        internal_black_pieces = [(square, piece) for square, piece in internal_board.items() 
                               if piece.get('color') == 'black']
        print(f"\nInternal board has {len(internal_black_pieces)} black pieces")
        
        # Check if there's a serialization issue
        print("\nComparing internal board to response board:")
        for square, piece in internal_board.items():
            if piece.get('color') == 'black':
                response_piece = board_dict.get(square)
                print(f"Internal: {square}: {piece}")
                print(f"Response: {square}: {response_piece}")
                if response_piece:
                    print(f"Colors match: {piece.get('color') == response_piece.get('color')}")
                    break
    
    # Count the occurrences of 'black' in the raw response
    raw_response_str = str(response.data)
    black_count = raw_response_str.count('"color": "black"')
    total_black_count = raw_response_str.count('black')
    
    print(f"\nCounts in raw response:")
    print(f"'\"color\": \"black\"' occurrences: {black_count}")
    print(f"Total 'black' occurrences: {total_black_count}")
    
    # Try to identify any other contexts where 'black' appears
    if black_count != total_black_count:
        print(f"\nOther contexts where 'black' appears:")
        # Find indices where 'black' appears
        indices = [i for i in range(len(raw_response_str)) 
                  if raw_response_str[i:i+5] == 'black']
        
        for i in indices:
            # Get some context around the occurrence
            start = max(0, i - 20)
            end = min(len(raw_response_str), i + 25)
            context = raw_response_str[start:end]
            print(f"Context: ...{context}...")

if __name__ == "__main__":
    test_board_serialization() 