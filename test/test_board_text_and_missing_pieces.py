import unittest
import json
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class BoardTextAndMissingPiecesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_black_rook_and_h_pawn_present(self):
        """Test that black rook on a8 and black pawn on h7 are present."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Specifically check for black rook at a8
        self._verify_piece_exists(init_board, 'a8', 'r', 'black', "Black rook missing from a8")
        
        # Specifically check for black pawn at h7
        self._verify_piece_exists(init_board, 'h7', 'p', 'black', "Black h pawn missing from h7")
        
        # Make a few moves to ensure pieces remain visible after moves
        moves = [
            ('e2', 'e4'),  # White pawn
            ('e7', 'e5'),  # Black pawn
            ('g1', 'f3'),  # White knight
        ]
        
        for from_square, to_square in moves:
            move_response = self.client.post('/move',
                                   data=json.dumps({"from": from_square, "to": to_square}),
                                   content_type='application/json')
            move_data = move_response.get_json()
            board = move_data['board']
            
            # Continue to check for black rook and h pawn after moves
            self._verify_piece_exists(board, 'a8', 'r', 'black', f"Black rook missing from a8 after move {from_square}-{to_square}")
            self._verify_piece_exists(board, 'h7', 'p', 'black', f"Black h pawn missing from h7 after move {from_square}-{to_square}")
    
    def test_all_white_pieces_present(self):
        """Test that all white pieces are present on the board."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Check all white pieces
        white_pieces = [
            ('a1', 'r', 'White rook missing from a1'),
            ('b1', 'n', 'White knight missing from b1'),
            ('c1', 'b', 'White bishop missing from c1'),
            ('d1', 'q', 'White queen missing from d1'),
            ('e1', 'k', 'White king missing from e1'),
            ('f1', 'b', 'White bishop missing from f1'),
            ('g1', 'n', 'White knight missing from g1'),
            ('h1', 'r', 'White rook missing from h1')
        ]
        
        for square, piece_type, message in white_pieces:
            self._verify_piece_exists(init_board, square, piece_type, 'white', message)
        
        # Check white pawns
        for file_char in 'abcdefgh':
            square = f"{file_char}2"
            self._verify_piece_exists(init_board, square, 'p', 'white', f"White pawn missing from {square}")
        
    def test_no_black_text_on_squares(self):
        """Test that 'black' text is not appearing on the board squares."""
        # This test verifies the correct transmission of piece data 
        # to prevent 'black' text appearing on squares
        
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Check that all pieces have proper data structure that won't result in raw text display
        for square, piece_data in init_board.items():
            # Validate piece data structure
            self.assertIn('type', piece_data, f"Piece at {square} missing 'type' attribute")
            self.assertIn('color', piece_data, f"Piece at {square} missing 'color' attribute")
            
            # Validate data types to ensure rendering will work
            self.assertIsInstance(piece_data['type'], str, f"Piece type at {square} should be a string")
            self.assertIsInstance(piece_data['color'], str, f"Piece color at {square} should be a string")
            
            # Check that piece type is a single character
            self.assertEqual(len(piece_data['type']), 1, f"Piece type at {square} should be a single character")
            
            # Check that color is either 'white' or 'black'
            self.assertIn(piece_data['color'], ['white', 'black'], 
                         f"Piece color at {square} should be 'white' or 'black', got '{piece_data['color']}'")
    
    def _verify_piece_exists(self, board, square, expected_type, expected_color, message):
        """Verify that a piece exists at the specified square with the correct type and color."""
        self.assertIn(square, board, f"No piece at {square}: {message}")
        
        piece = board[square]
        self.assertEqual(piece['type'], expected_type, 
                         f"Expected {expected_color} {expected_type} at {square}, but found {piece['type']}: {message}")
        self.assertEqual(piece['color'], expected_color, 
                         f"Expected {expected_color} piece at {square}, but found {piece['color']}: {message}") 