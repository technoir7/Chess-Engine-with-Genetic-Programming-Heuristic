from flask import Flask, render_template, request, jsonify
import json
import os
import re
from chess_logic_by_thomasahle import Position, initial, MATE_LOWER, MATE_UPPER
from minimax import Minimax
from genetic_programming import evolve, tournament, makerandomtree

# Move our utils functions directly into app.py to avoid circular imports
def is_king_in_check(position, side='black'):
    """
    Determine if the king of the specified side is in check.
    
    Args:
        position: A Position object
        side: 'white' or 'black' - which king to check
    
    Returns:
        bool: True if the king is in check, False otherwise
    """
    # If checking black king, we need to rotate the position
    # This is because the gen_moves function generates moves for the upper case pieces (white)
    if side == 'black':
        position = position.rotate()
    
    # Find the king's position
    king_square = None
    for i, piece in enumerate(position.board):
        if piece == 'K':  # Look for white king
            king_square = i
            break
    
    if king_square is None:
        return False  # No king found
    
    # Rotate to check opponent's moves
    rotated_pos = position.rotate()
    
    # Check if any of the opponent's moves can capture the king
    for i, j in rotated_pos.gen_moves():
        if j == 119 - king_square:  # The opponent can capture our king
            return True
    
    return False

def is_checkmate(position, side='white'):
    """
    Determine if the specified side is in checkmate.
    
    Args:
        position: A Position object
        side: 'white' or 'black' - which side to check for checkmate
    
    Returns:
        bool: True if the side is in checkmate, False otherwise
    """
    # If checking black, we need to rotate
    if side == 'black':
        position = position.rotate()
    
    # First check if the king is in check
    if not is_king_in_check(position):
        return False  # Not in check, so not checkmate
    
    # Now check if there are any legal moves that can get out of check
    # In a valid chess position, if there are no moves and the king is in check, it's checkmate
    moves = list(position.gen_moves())
    if not moves:
        return True  # No moves and in check = checkmate
    
    # For each move, check if it gets us out of check
    for move in moves:
        new_pos = position.move(move)
        # After move, it's opponent's turn, so we need to check if they can capture our king
        if not is_king_in_check(new_pos.rotate(), 'black'):
            return False  # Found at least one move that gets out of check
    
    # If no move gets us out of check, it's checkmate
    return True

def is_stalemate(position, side='white'):
    """
    Determine if the specified side is in stalemate.
    
    Args:
        position: A Position object
        side: 'white' or 'black' - which side to check for stalemate
    
    Returns:
        bool: True if the side is in stalemate, False otherwise
    """
    # If checking black, we need to rotate
    if side == 'black':
        position = position.rotate()
    
    # First check if the king is in check
    if is_king_in_check(position):
        return False  # In check, so not stalemate
    
    # Now check if there are any legal moves
    # In a valid chess position, if there are no moves and the king is not in check, it's stalemate
    moves = list(position.gen_moves())
    if not moves:
        return True  # No moves and not in check = stalemate
    
    return False  # Has moves, so not stalemate

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
    global current_position, current_player, move_history
    
    data = request.json
    from_square = data.get('from')
    to_square = data.get('to')
    
    if not from_square or not to_square:
        return jsonify({
            'valid': False,
            'message': 'Missing from or to square',
            'currentPlayer': current_player
        })
    
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
    new_position = current_position.move(player_move)
    
    # Verify that the move doesn't leave the player's king in check
    # This is needed because the engine doesn't check for this
    if is_king_in_check(new_position.rotate(), 'white'):
        print(f"Move rejected: Would leave king in check {from_square}-{to_square}")
        return jsonify({
            'valid': False,
            'message': 'Invalid move - would leave your king in check',
            'board': board_to_dict(current_position),
            'gameState': 'active',
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player  # No change in turn
        })
    
    # If we get here, the move is valid and doesn't leave the king in check
    current_position = new_position
    
    # Record the move
    move_history.append({
        'from': from_square,
        'to': to_square,
        'player': 'white'
    })
    
    # Update current player
    current_player = 'black'
    print(f"Player move accepted. Turn changed to: {current_player}")
    
    # Check if the player won (checkmate)
    if is_checkmate(current_position, 'black'):
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'player',
            'message': 'Checkmate! You won!',
            'board': board_to_dict(current_position),
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player
        })
    
    # Check for stalemate
    if is_stalemate(current_position, 'black'):
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'draw',
            'message': 'Stalemate! Game ends in a draw.',
            'board': board_to_dict(current_position),
            'moves': format_moves_for_frontend(move_history),
            'currentPlayer': current_player
        })
    
    # AI makes a move
    ai_move, score = searcher.search(current_position, secs=1.5)
    
    # Check if AI has valid moves
    if ai_move is None:
        # If AI has no valid moves, check if it's in check (checkmate) or not (stalemate)
        if is_king_in_check(current_position, 'black'):
            return jsonify({
                'valid': True,
                'gameState': 'ended',
                'winner': 'player',
                'message': 'Checkmate! You won!',
                'board': board_to_dict(current_position),
                'moves': format_moves_for_frontend(move_history),
                'currentPlayer': current_player
            })
        else:
            return jsonify({
                'valid': True,
                'gameState': 'ended',
                'winner': 'draw',
                'message': 'Stalemate! Game ends in a draw.',
                'board': board_to_dict(current_position),
                'moves': format_moves_for_frontend(move_history),
                'currentPlayer': current_player
            })
    
    # If we get here, AI has a valid move
    from_ai_coord, to_ai_coord = ai_move
    from_ai_square = coord_to_square(from_ai_coord)
    to_ai_square = coord_to_square(to_ai_coord)
    
    # Make the AI's move
    current_position = current_position.move(ai_move)
    
    # Record the AI move
    move_history.append({
        'from': from_ai_square,
        'to': to_ai_square,
        'player': 'black'
    })
    
    # Update current player back to white
    current_player = 'white'
    print(f"AI move: {from_ai_square}-{to_ai_square}. Turn changed to: {current_player}")
    
    # Check if AI won (checkmate)
    if is_checkmate(current_position, 'white'):
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'ai',
            'message': 'Checkmate! AI won!',
            'board': board_to_dict(current_position),
            'moves': format_moves_for_frontend(move_history),
            'aiMove': {
                'from': from_ai_square,
                'to': to_ai_square
            },
            'currentPlayer': current_player
        })
    
    # Check for stalemate
    if is_stalemate(current_position, 'white'):
        return jsonify({
            'valid': True,
            'gameState': 'ended',
            'winner': 'draw',
            'message': 'Stalemate! Game ends in a draw.',
            'board': board_to_dict(current_position),
            'moves': format_moves_for_frontend(move_history),
            'aiMove': {
                'from': from_ai_square,
                'to': to_ai_square
            },
            'currentPlayer': current_player
        })
    
    # Return successful move
    return jsonify({
        'valid': True,
        'message': 'Move successful',
        'gameState': 'active',
        'board': board_to_dict(current_position),
        'moves': format_moves_for_frontend(move_history),
        'aiMove': {
            'from': from_ai_square,
            'to': to_ai_square
        },
        'currentPlayer': current_player  # Make sure this is included
    })

def format_moves_for_frontend(moves):
    """
    Format moves for the frontend, ensuring they are all valid.
    
    Args:
        moves: A list of move dictionaries with 'from', 'to', and 'player' keys
        
    Returns:
        A list of validated move dictionaries
    """
    # Ensure we have a valid list of moves
    if not moves:
        return []
    
    # Get the current board state to validate against
    current_board = board_to_dict(current_position)
    
    # Create a list to hold validated moves
    validated_moves = []
    
    for move in moves:
        # Basic validation of move format
        if not all(key in move for key in ['from', 'to', 'player']):
            print(f"WARNING: Invalid move format: {move}")
            continue
        
        # Basic validation of square format
        from_square = move['from']
        to_square = move['to']
        
        if not re.match(r'^[a-h][1-8]$', from_square) or not re.match(r'^[a-h][1-8]$', to_square):
            print(f"WARNING: Invalid square format in move: {move}")
            continue
        
        # Add to validated moves
        validated_moves.append(move)
    
    return validated_moves

# Helper function to convert board to dictionary representation for the frontend
def board_to_dict(position):
    """
    Convert a Position object's board representation to a dictionary 
    with chess square notation (e.g., 'e4') as keys.
    
    Args:
        position: A Position object
        
    Returns:
        dict: A dictionary mapping chess square notation to piece information
    """
    result = {}
    
    # Map of piece characters to piece types
    piece_types = {
        'P': 'pawn', 'N': 'knight', 'B': 'bishop', 
        'R': 'rook', 'Q': 'queen', 'K': 'king',
        'p': 'pawn', 'n': 'knight', 'b': 'bishop', 
        'r': 'rook', 'q': 'queen', 'k': 'king'
    }
    
    # Track king positions to ensure there's exactly one of each
    white_king_found = False
    black_king_found = False
    
    # Iterate through the 10x12 board (which includes borders)
    for i, p in enumerate(position.board):
        # Skip spaces and newlines (borders and padding)
        if p == ' ' or p == '\n' or p == '.':
            continue
        
        # Get the piece type and color
        if p in piece_types:
            piece_type = piece_types[p]
            color = 'white' if p.isupper() else 'black'
            
            # Check for duplicate kings
            if piece_type == 'king':
                if color == 'white' and white_king_found:
                    print(f"WARNING: Multiple white kings found! Skipping duplicate at position {i}")
                    continue
                elif color == 'black' and black_king_found:
                    print(f"WARNING: Multiple black kings found! Skipping duplicate at position {i}")
                    continue
                
                # Mark that we found a king
                if color == 'white':
                    white_king_found = True
                else:
                    black_king_found = True
            
            # Try to convert the position to square notation
            try:
                square = coord_to_square(i)
                # Only add the piece if the square is valid
                if square and re.match(r'^[a-h][1-8]$', square):
                    result[square] = {
                        'type': piece_type,
                        'color': color
                    }
                    print(f"Mapped piece at {i} to {square}: {color} {piece_type}")
                else:
                    print(f"WARNING: Invalid square {square} for piece at position {i}")
            except Exception as e:
                print(f"ERROR: Failed to convert position {i} to square notation: {str(e)}")
        else:
            # If the piece character is not recognized, log a warning
            if p not in [' ', '\n', '.']:
                print(f"WARNING: Unknown piece character '{p}' at position {i}")
    
    # Debug output for tracking piece data
    for square, piece in result.items():
        print(f"Final piece mapping - {square}: {piece['color']} {piece['type']}")
    
    # Ensure each king exists
    if not white_king_found:
        print("WARNING: No white king found on the board!")
    if not black_king_found:
        print("WARNING: No black king found on the board!")
    
    return result

# Convert algebraic notation to internal coordinate
def square_to_coord(square):
    """Convert algebraic notation (e.g., 'e4') to the engine's internal coordinate."""
    if not square or len(square) != 2:
        print(f"Warning: Invalid square notation '{square}'")
        return None
        
    file_char, rank_char = square[0], square[1]
    file_idx = ord(file_char) - ord('a')  # 'a' -> 0, 'b' -> 1, etc.
    rank_idx = 8 - int(rank_char)         # '1' -> 7, '2' -> 6, etc.
    
    # Validate indices are within bounds
    if file_idx < 0 or file_idx > 7 or rank_idx < 0 or rank_idx > 7:
        print(f"Warning: Square {square} is out of bounds")
        return None
    
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
    
    # Input validation
    if coord < 21 or coord > 98:
        print(f"Warning: Coord {coord} is outside valid range 21-98")
        # Default to a sensible value to avoid crashing
        coord = 21  # Default to A8
    
    # Calculate indices from coord 
    # Correct calculation based on the 10x12 board with padding
    rank_idx = (coord - 21) // 10
    file_idx = (coord % 10) - 1
    
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