import unittest
import json
from app import app, board_to_dict, _generate_standard_initial_board
from chess_logic_by_thomasahle import Position, initial

class MissingPiecesFixTest(unittest.TestCase):
    """Test case specifically for the fixes addressing missing pieces."""
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_h8_rook_present(self):
        """Test that the black rook is present at h8."""
        # Initialize the game
        response = self.client.post('/initialize',
                                    data='{"difficulty": "medium"}',
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200, "Initialize request should succeed")
        
        data = response.get_json()
        board = data['board']
        
        # Verify h8 has a black rook
        self.assertIn('h8', board, "h8 should be in the board")
        h8_piece = board['h8']
        self.assertEqual(h8_piece['color'], 'black', "h8 piece should be black")
        self.assertEqual(h8_piece['type'], 'r', "h8 piece should be a rook")
    
    def test_h7_pawn_present(self):
        """Test that the black pawn is present at h7."""
        # Initialize the game
        response = self.client.post('/initialize',
                                    data='{"difficulty": "medium"}',
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200, "Initialize request should succeed")
        
        data = response.get_json()
        board = data['board']
        
        # Verify h7 has a black pawn
        self.assertIn('h7', board, "h7 should be in the board")
        h7_piece = board['h7']
        self.assertEqual(h7_piece['color'], 'black', "h7 piece should be black")
        self.assertEqual(h7_piece['type'], 'p', "h7 piece should be a pawn")
    
    def test_all_white_pieces_present(self):
        """Test that all white pieces are present."""
        # Initialize the game
        response = self.client.post('/initialize',
                                    data='{"difficulty": "medium"}',
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200, "Initialize request should succeed")
        
        data = response.get_json()
        board = data['board']
        
        # Check for white back rank pieces
        back_rank = ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1']
        piece_types = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        
        for i, square in enumerate(back_rank):
            self.assertIn(square, board, f"{square} should be in the board")
            piece = board[square]
            self.assertEqual(piece['color'], 'white', f"{square} piece should be white")
            self.assertEqual(piece['type'], piece_types[i], f"{square} piece should be {piece_types[i]}")
        
        # Check for white pawns
        for file_char in 'abcdefgh':
            square = f"{file_char}2"
            self.assertIn(square, board, f"{square} should be in the board")
            piece = board[square]
            self.assertEqual(piece['color'], 'white', f"{square} piece should be white")
            self.assertEqual(piece['type'], 'p', f"{square} piece should be a pawn")
    
    def test_coordinate_conversion(self):
        """Test that square to coordinate conversion and back works correctly."""
        from app import square_to_coord, coord_to_square
        
        # Test a few critical squares
        test_squares = ['a1', 'h1', 'a8', 'h8', 'e4']
        
        for square in test_squares:
            coords = square_to_coord(square)
            back_to_square = coord_to_square(coords)
            self.assertEqual(square, back_to_square, 
                            f"Converting {square} to coords and back should return {square}, got {back_to_square}")
    
    def test_board_to_dict_returns_correct_pieces(self):
        """Test that board_to_dict returns all 32 pieces with correct coordinates."""
        # Create a position with the initial board setup
        position = Position(initial, 0, (True, True), (True, True), 0, 0)
        
        # Convert to dictionary
        board_dict = board_to_dict(position)
        
        # Check that we have exactly 32 pieces
        self.assertEqual(len(board_dict), 32, "board_to_dict should return exactly 32 pieces")
        
        # Check for key pieces
        self.assertIn('h8', board_dict, "Black rook at h8 should be present")
        self.assertEqual(board_dict['h8']['color'], 'black', "h8 piece should be black")
        self.assertEqual(board_dict['h8']['type'], 'r', "h8 piece should be a rook")
        
        self.assertIn('h7', board_dict, "Black pawn at h7 should be present")
        self.assertEqual(board_dict['h7']['color'], 'black', "h7 piece should be black")
        self.assertEqual(board_dict['h7']['type'], 'p', "h7 piece should be a pawn")
        
        # Check for white pieces
        white_squares = [f"{f}{r}" for f in "abcdefgh" for r in "12"]
        for square in white_squares:
            self.assertIn(square, board_dict, f"White piece at {square} should be present")
            self.assertEqual(board_dict[square]['color'], 'white', f"Piece at {square} should be white")

if __name__ == '__main__':
    unittest.main() 