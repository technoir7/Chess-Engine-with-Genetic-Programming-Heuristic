"""Utility functions for chess engine testing."""

import re
import sys
import os

# Add the parent directory to the path so we can import from there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chess_logic_by_thomasahle import Position, initial
from app import board_to_dict

def create_custom_position(board_str):
    """
    Create a custom chess position from a string representation.
    
    Args:
        board_str: An 8x8 string representation of the board with:
                   - Uppercase letters for white pieces (K,Q,R,B,N,P)
                   - Lowercase letters for black pieces (k,q,r,b,n,p)
                   - . or spaces for empty squares
    
    Returns:
        A Position object with the requested board state
    """
    # Clean up and standardize the input
    board_str = board_str.replace(' ', '.')
    lines = board_str.strip().split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    # Ensure we have 8 lines
    if len(lines) != 8:
        raise ValueError(f"Board should have 8 rows, got {len(lines)}")
    
    # Ensure each line has 8 characters
    for i, line in enumerate(lines):
        if len(line) != 8:
            raise ValueError(f"Row {i+1} should have 8 squares, got {len(line)}")
    
    # Create the thomasahle-format board (10x12 with borders)
    thomasahle_board = []
    thomasahle_board.append('         \n')  # Top border
    
    for line in lines:
        thomasahle_board.append(' ' + line + ' \n')  # Add side borders
    
    thomasahle_board.append('         \n')  # Bottom border
    
    # Join into a single string
    board = ''.join(thomasahle_board)
    
    # Create a Position object with this board
    position = Position(board, 0, (True, True), (True, True), 0, 0)
    
    return position

def is_position_valid(position):
    """
    Check if a position is valid by verifying pieces are on valid squares.
    
    Args:
        position: A Position object to check
    
    Returns:
        bool: True if the position is valid, False otherwise
        str: Description of the issue if invalid
    """
    board_dict = board_to_dict(position)
    
    # Check that each piece is on a valid square
    for square, piece_info in board_dict.items():
        if not re.match(r'^[a-h][1-8]$', square):
            return False, f"Invalid square: {square}"
    
    # Verify there's exactly one king of each color
    white_king_count = 0
    black_king_count = 0
    
    for square, piece_info in board_dict.items():
        if piece_info['type'] == 'king':
            if piece_info['color'] == 'white':
                white_king_count += 1
            else:
                black_king_count += 1
    
    if white_king_count != 1:
        return False, f"Position has {white_king_count} white kings, should have exactly 1"
    
    if black_king_count != 1:
        return False, f"Position has {black_king_count} black kings, should have exactly 1"
    
    return True, "Position is valid"

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