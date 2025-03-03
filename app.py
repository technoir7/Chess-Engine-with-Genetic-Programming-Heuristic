from flask import Flask, render_template, request, jsonify
import json
import os
from chess_logic_by_thomasahle import Position, initial, MATE_LOWER, MATE_UPPER
from minimax import Minimax
from genetic_programming import evolve, tournament, makerandomtree

app = Flask(__name__)

# Global variable to store the current chess position and AI
current_position = Position(initial, 0, (True,True), (True,True), 0, 0)
heuristic = None
searcher = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize_game():
    global current_position, heuristic, searcher
    
    # Reset the board
    current_position = Position(initial, 0, (True,True), (True,True), 0, 0)
    
    # Get difficulty level from request (default to medium)
    data = request.get_json()
    difficulty = data.get('difficulty', 'medium')
    
    # Set AI parameters based on difficulty
    if difficulty == 'easy':
        depth = 2
        time = 1
    elif difficulty == 'medium':
        depth = 3
        time = 1.5
    else:  # hard
        depth = 4
        time = 2
    
    # Initialize or use existing heuristic
    if heuristic is None:
        # For quick startup, use a random tree initially
        heuristic = makerandomtree(3, current_position)
    
    # Initialize the searcher with our heuristic
    searcher = Minimax(heuristic)
    
    # Get the board representation
    board_representation = board_to_dict(current_position)
    
    # Log the board state for debugging
    print("Initial board state:")
    for square, piece_info in board_representation.items():
        print(f"{square}: {piece_info['color']} {piece_info['type']}")
    
    # Return the initial board state
    return jsonify({
        'board': board_representation,
        'gameState': 'active',
        'message': f'Game started with {difficulty} difficulty'
    })

@app.route('/evolve', methods=['POST'])
def evolve_ai():
    global heuristic, searcher, current_position
    
    data = request.get_json()
    generations = int(data.get('generations', 10))
    
    # Reset the position for evolution
    pos = Position(initial, 0, (True,True), (True,True), 0, 0)
    
    # Evolve a new heuristic
    heuristic = evolve(pos, 5, 2, tournament, maxgen=generations)
    
    # Update the searcher with the new heuristic
    searcher = Minimax(heuristic)
    
    return jsonify({
        'message': f'AI evolved over {generations} generations',
        'success': True
    })

@app.route('/move', methods=['POST'])
def make_move():
    global current_position, searcher
    
    data = request.get_json()
    from_square = data.get('from')
    to_square = data.get('to')
    
    # Convert frontend coordinates to engine coordinates
    from_coord = square_to_coord(from_square)
    to_coord = square_to_coord(to_square)
    
    # Create the move tuple
    player_move = (from_coord, to_coord)
    
    # Check if the move is valid
    valid_moves = current_position.gen_moves()
    if player_move not in valid_moves:
        return jsonify({
            'valid': False,
            'message': 'Invalid move',
            'board': board_to_dict(current_position)
        })
    
    # Make the player's move
    current_position = current_position.move(player_move)
    
    # Check if the player won
    if current_position.score <= -MATE_LOWER:
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'player',
            'message': 'You won!',
            'board': board_to_dict(current_position)
        })
    
    # AI makes a move
    ai_move, score = searcher.search(current_position, secs=1.5)
    current_position = current_position.move(ai_move)
    
    response = {
        'valid': True,
        'aiMove': {
            'from': coord_to_square(ai_move[0]),
            'to': coord_to_square(ai_move[1])
        },
        'board': board_to_dict(current_position),
        'gameState': 'active'
    }
    
    # Check if AI won
    if current_position.score <= -MATE_LOWER:
        response['gameState'] = 'ended'
        response['winner'] = 'ai'
        response['message'] = 'AI won!'
    
    # Check for checkmate by AI
    elif score == MATE_UPPER:
        response['gameState'] = 'ended'
        response['winner'] = 'ai'
        response['message'] = 'Checkmate!'
    
    return jsonify(response)

# Helper function to convert board to dictionary representation for the frontend
def board_to_dict(position):
    board_dict = {}
    for i in range(120):
        if i & 0x88 == 0:  # Check if it's a valid square
            file_idx = i & 7
            rank_idx = i >> 4
            square = f"{chr(97 + file_idx)}{8 - rank_idx}"
            piece = position.board[i]
            if piece != '.':
                color = 'white' if piece.isupper() else 'black'
                board_dict[square] = {
                    'type': piece.lower(),
                    'color': color
                }
    
    # Debug output
    print("Board representation:")
    for rank in range(8):
        row = []
        for file in range(8):
            square = f"{chr(97 + file)}{8 - rank}"
            if square in board_dict:
                piece = board_dict[square]
                row.append(f"{piece['color'][0]}{piece['type']}")
            else:
                row.append("__")
        print(" ".join(row))
    
    return board_dict

# Convert algebraic notation to internal coordinate
def square_to_coord(square):
    file_char, rank_char = square[0], square[1]
    file_idx = ord(file_char) - ord('a')
    rank_idx = 8 - int(rank_char)
    coord = file_idx + (rank_idx << 4)
    print(f"Converting square {square} to coord {coord}")
    return coord

# Convert internal coordinate to algebraic notation
def coord_to_square(coord):
    file_idx = coord & 7
    rank_idx = coord >> 4
    square = f"{chr(97 + file_idx)}{8 - rank_idx}"
    print(f"Converting coord {coord} to square {square}")
    return square

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Get host from environment variable or use default
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Get debug mode from environment variable or use default
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', 't', '1')
    
    print(f"Starting Genetic Chess Engine on {host}:{port} (debug={debug})")
    print("Use the following environment variables to customize:")
    print("  - PORT: Change the port (default: 5000)")
    print("  - HOST: Change the host (default: 0.0.0.0)")
    print("  - DEBUG: Enable debug mode (default: False)")
    print(f"\nOpen your browser to http://localhost:{port}/")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=debug, host=host, port=port) 