#!/usr/bin/env python
import json
from flask import Flask, jsonify
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

def debug_json_format():
    """Debug and fix the JSON format issue with black pieces"""
    # Create a test client
    client = app.test_client()
    
    # Initialize a game through the API
    response = client.post('/initialize',
                          data=json.dumps({'difficulty': 'medium'}),
                          content_type='application/json')
    
    # Get the response data
    data = response.get_json()
    board_dict = data.get('board', {})
    
    # Debug: Examine the raw response vs. Python object
    print("\nComparing Raw to Parsed:")
    board_str_raw = str(response.data)
    print(f"Raw board string (excerpt): {board_str_raw[:200]}...")
    
    # Re-serialize the board dict to JSON with json.dumps
    board_str_dumps = json.dumps(board_dict)
    print(f"Python dumps version (excerpt): {board_str_dumps[:200]}...")
    
    # Count occurrences in each string
    print("\nCounting occurrences:")
    raw_black_count = board_str_raw.count('black')
    raw_color_black_count = board_str_raw.count('"color":"black"')
    raw_color_space_black_count = board_str_raw.count('"color": "black"')
    print(f"Raw 'black' count: {raw_black_count}")
    print(f"Raw '\"color\":\"black\"' count: {raw_color_black_count}")
    print(f"Raw '\"color\": \"black\"' count: {raw_color_space_black_count}")
    
    dumps_black_count = board_str_dumps.count('black')
    dumps_color_black_count = board_str_dumps.count('"color":"black"')
    dumps_color_space_black_count = board_str_dumps.count('"color": "black"')
    print(f"Dumps 'black' count: {dumps_black_count}")
    print(f"Dumps '\"color\":\"black\"' count: {dumps_color_black_count}")
    print(f"Dumps '\"color\": \"black\"' count: {dumps_color_space_black_count}")
    
    # Check if we need to modify the test
    if raw_black_count > 0 and raw_color_black_count == 0 and raw_color_space_black_count == 0:
        print("\nIssue detected: 'black' appears in the raw response but not in the expected format")
        # Try to find where 'black' appears
        index = board_str_raw.find('black')
        if index > 0:
            # Get context
            context_start = max(0, index - 20)
            context_end = min(len(board_str_raw), index + 20)
            context = board_str_raw[context_start:context_end]
            print(f"Context around 'black': {context}")
    
    # Examine one black piece directly
    black_pieces = {square: piece for square, piece in board_dict.items() 
                   if piece.get('color') == 'black'}
    if black_pieces:
        sample_square = next(iter(black_pieces))
        sample_piece = black_pieces[sample_square]
        print(f"\nSample black piece: {sample_square}: {sample_piece}")
        serialized = json.dumps({sample_square: sample_piece})
        print(f"Serialized: {serialized}")
        print(f"Contains 'black': {serialized.count('black')}")
        print(f"Contains '\"color\":\"black\"': {serialized.count('\"color\":\"black\"')}")
    
    # Check and fix app behavior
    print("\nTrying different JSON serialization approaches:")
    position = Position(initial, 0, (True,True), (True,True), 0, 0)
    board = board_to_dict(position)
    
    # Standard Python json dumps
    standard_json = json.dumps(board)
    print(f"Standard json.dumps - 'black' count: {standard_json.count('black')}")
    print(f"Standard json.dumps - '\"color\":\"black\"' count: {standard_json.count('\"color\":\"black\"')}")
    
    # Flask jsonify
    with app.app_context():
        flask_json = jsonify(board).get_data(as_text=True)
    print(f"Flask jsonify - 'black' count: {flask_json.count('black')}")
    print(f"Flask jsonify - '\"color\":\"black\"' count: {flask_json.count('\"color\":\"black\"')}")
    
    # Check API handling in Flask route
    print("\nChecking the Response object from Flask:")
    for key, value in response.__dict__.items():
        if isinstance(value, (str, bytes)) and 'black' in str(value):
            print(f"Found 'black' in response.{key}")
    
    # Solution: Fix the test to account for how Flask serializes JSON
    print("\nSolution:")
    print("1. Update the test to check the presence of black pieces directly in Python objects")
    print("2. Check the raw response data format to match how Flask is serializing the JSON")

if __name__ == "__main__":
    debug_json_format() 