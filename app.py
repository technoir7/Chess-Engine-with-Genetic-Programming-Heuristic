from flask import Flask, render_template, request, jsonify
import json
import os
from chess_logic_by_thomasahle import Position, initial, MATE_LOWER, MATE_UPPER
from minimax import Minimax
from genetic_programming import evolve, tournament, makerandomtree

app = Flask(__name__)

# Global variables to store the current chess position, AI, and game state
current_position = Position(initial, 0, (True,True), (True,True), 0, 0)
heuristic = None
searcher = None
move_history = []  # Track all moves made
current_player = 'white'  # Track whose turn it is (white = player, black = AI)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize_game():
    global current_position, heuristic, searcher, move_history, current_player
    
    # Reset the board
    current_position = Position(initial, 0, (True,True), (True,True), 0, 0)
    
    # Reset move history and current player
    move_history = []
    current_player = 'white'  # Always start with white (player)
    
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
        'message': f'Game started with {difficulty} difficulty',
        'currentPlayer': current_player  # Include current player in response
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
    global current_position, searcher, move_history, current_player
    
    data = request.get_json()
    from_square = data.get('from')
    to_square = data.get('to')
    
    # Debug output for tracking turn state
    print(f"Current player: {current_player}, Move request: {from_square}-{to_square}")
    
    # TESTING PURPOSE ONLY: Allow forcing current_player to 'black' for tests
    # This is used in test_shift_and_auto_move_issues.py to test turn handling
    if data.get('_forceBlackTurn'):
        print("TEST MODE: Forcing turn to 'black' for testing purposes")
        current_player = 'black'
    
    # Check if it's the player's turn - strictly enforce this
    if current_player != 'white':
        print(f"Move rejected: Not player's turn (current turn: {current_player})")
        return jsonify({
            'valid': False,
            'message': f"Not your turn. Current turn: {current_player}",
            'board': board_to_dict(current_position),
            'gameState': 'active',
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player
        })
    
    # Convert frontend coordinates to engine coordinates
    from_coord = square_to_coord(from_square)
    to_coord = square_to_coord(to_square)
    
    # Create the move tuple
    player_move = (from_coord, to_coord)
    
    # Check if the move is valid
    valid_moves = list(current_position.gen_moves())
    if player_move not in valid_moves:
        print(f"Move rejected: Invalid move {from_square}-{to_square}")
        return jsonify({
            'valid': False,
            'message': 'Invalid move',
            'board': board_to_dict(current_position),
            'gameState': 'active',
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player  # No change in turn
        })
    
    # Make the player's move
    current_position = current_position.move(player_move)
    
    # Record the move
    move_history.append({
        'from': from_square,
        'to': to_square,
        'player': 'white'
    })
    
    # Update current player
    current_player = 'black'
    print(f"Player move accepted. Turn changed to: {current_player}")
    
    # Check if the player won
    if current_position.score <= -MATE_LOWER:
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'player',
            'message': 'You won!',
            'board': board_to_dict(current_position),
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player
        })
    
    # AI makes a move
    ai_move, score = searcher.search(current_position, secs=1.5)
    
    # Check if AI has valid moves
    if ai_move is None:
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'player',
            'message': 'AI has no valid moves. You won!',
            'board': board_to_dict(current_position),
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player
        })
    
    # Make AI move
    current_position = current_position.move(ai_move)
    
    # Record AI move
    ai_from_square = coord_to_square(ai_move[0])
    ai_to_square = coord_to_square(ai_move[1]) 
    move_history.append({
        'from': ai_from_square,
        'to': ai_to_square,
        'player': 'black'
    })
    
    # Update current player
    current_player = 'white'
    print(f"AI move made. Turn changed to: {current_player}")
    
    response = {
        'valid': True,
        'aiMove': {
            'from': ai_from_square,
            'to': ai_to_square
        },
        'board': board_to_dict(current_position),
        'gameState': 'active',
        'moves': format_moves_for_frontend(move_history),
        'currentPlayer': current_player
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
    
    # Check if player has any valid moves
    elif not current_position.gen_moves():
        response['gameState'] = 'ended'
        response['winner'] = 'ai'
        response['message'] = 'No valid moves. AI won!'
    
    return jsonify(response)

# Helper function to convert move history to frontend format
def format_moves_for_frontend(moves):
    return moves

# Helper function to convert board to dictionary representation for the frontend
def board_to_dict(position):
    board_dict = {}
    
    # For debugging, print the raw board string
    # print("Raw board string:")
    # print(position.board)
    
    # The board is represented as a string with newlines, split it into rows
    rows = position.board.split('\n')
    # Skip the first two and last two rows (padding)
    board_rows = rows[2:10]
    
    for rank_idx, row in enumerate(board_rows):
        # Skip the first space character
        row = row[1:]
        for file_idx, piece in enumerate(row):
            if piece != '.':
                # Convert to algebraic notation (a1, b2, etc.)
                square = f"{chr(97 + file_idx)}{8 - rank_idx}"
                
                # Map the piece character to its color
                # Note: In the rotated position, the case is swapped
                # So uppercase means black and lowercase means white
                # We need to convert this back to the normal convention
                if piece.isupper():
                    color = 'white'
                else:
                    color = 'black'
                
                # Map piece char to piece type for frontend
                piece_type = piece.lower()
                
                board_dict[square] = {
                    'type': piece_type,
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
    """Convert algebraic notation (e.g., 'e4') to the engine's internal coordinate."""
    file_char, rank_char = square[0], square[1]
    file_idx = ord(file_char) - ord('a')  # 'a' -> 0, 'b' -> 1, etc.
    rank_idx = 8 - int(rank_char)         # '1' -> 7, '2' -> 6, etc.
    
    # Board is represented as a 120-char string with padding
    # A1=91, H1=98, A8=21, H8=28
    # Each rank is 10 positions apart, each file is 1 position apart
    coord = 21 + file_idx + (10 * rank_idx)
    
    print(f"Converting square {square} to coord {coord}")
    return coord

# Convert internal coordinate to algebraic notation
def coord_to_square(coord):
    """Convert the engine's internal coordinate to algebraic notation (e.g., 'e4')."""
    # Board is represented as a 120-char string with padding
    # A1=91, H1=98, A8=21, H8=28
    # Convert from internal coordinates to file/rank
    file_idx = (coord % 10) - 1  # Subtract 1 because each row starts with a space
    rank_idx = (coord - 21) // 10
    
    # Ensure the indices are within valid range
    if file_idx < 0 or file_idx > 7 or rank_idx < 0 or rank_idx > 7:
        print(f"Warning: Invalid coord {coord} resulting in file_idx={file_idx}, rank_idx={rank_idx}")
        # Apply bounds to ensure we don't crash
        file_idx = max(0, min(file_idx, 7))
        rank_idx = max(0, min(rank_idx, 7))
    
    file_char = chr(97 + file_idx)
    rank_char = str(8 - rank_idx)
    
    square = f"{file_char}{rank_char}"
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