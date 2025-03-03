import unittest
import json
from app import app, board_to_dict, _generate_standard_initial_board
from chess_logic_by_thomasahle import Position, initial

class CompleteInitialBoardTest(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_standard_initial_board_has_all_pieces(self):
        """Test that _generate_standard_initial_board returns all 32 pieces."""
        standard_board = _generate_standard_initial_board()
        self.assertEqual(len(standard_board), 32, "Standard initial board should contain exactly 32 pieces")
        
        # Test all pieces are present with correct positions, types, and colors
        expected_pieces = {
            # White pieces
            'a1': {'color': 'white', 'type': 'r'},
            'b1': {'color': 'white', 'type': 'n'},
            'c1': {'color': 'white', 'type': 'b'},
            'd1': {'color': 'white', 'type': 'q'},
            'e1': {'color': 'white', 'type': 'k'},
            'f1': {'color': 'white', 'type': 'b'},
            'g1': {'color': 'white', 'type': 'n'},
            'h1': {'color': 'white', 'type': 'r'},
            'a2': {'color': 'white', 'type': 'p'},
            'b2': {'color': 'white', 'type': 'p'},
            'c2': {'color': 'white', 'type': 'p'},
            'd2': {'color': 'white', 'type': 'p'},
            'e2': {'color': 'white', 'type': 'p'},
            'f2': {'color': 'white', 'type': 'p'},
            'g2': {'color': 'white', 'type': 'p'},
            'h2': {'color': 'white', 'type': 'p'},
            
            # Black pieces
            'a8': {'color': 'black', 'type': 'r'},
            'b8': {'color': 'black', 'type': 'n'},
            'c8': {'color': 'black', 'type': 'b'},
            'd8': {'color': 'black', 'type': 'q'},
            'e8': {'color': 'black', 'type': 'k'},
            'f8': {'color': 'black', 'type': 'b'},
            'g8': {'color': 'black', 'type': 'n'},
            'h8': {'color': 'black', 'type': 'r'},
            'a7': {'color': 'black', 'type': 'p'},
            'b7': {'color': 'black', 'type': 'p'},
            'c7': {'color': 'black', 'type': 'p'},
            'd7': {'color': 'black', 'type': 'p'},
            'e7': {'color': 'black', 'type': 'p'},
            'f7': {'color': 'black', 'type': 'p'},
            'g7': {'color': 'black', 'type': 'p'},
            'h7': {'color': 'black', 'type': 'p'}
        }
        
        for square, expected in expected_pieces.items():
            self.assertIn(square, standard_board, f"Missing piece at {square}")
            self.assertEqual(expected['type'], standard_board[square]['type'], 
                           f"Incorrect piece type at {square}")
            self.assertEqual(expected['color'], standard_board[square]['color'], 
                           f"Incorrect piece color at {square}")
    
    def test_initial_board_conversion_has_all_pieces(self):
        """Test that converting the initial position includes all 32 pieces."""
        position = Position(initial, 0, (True,True), (True,True), 0, 0)
        board_dict = board_to_dict(position, use_full_words=False)
        
        # Verify we have all 32 pieces
        self.assertEqual(len(board_dict), 32, "Converted initial board should contain exactly 32 pieces")
        
        # Specifically check for previously missing pieces
        self.assertIn('h8', board_dict, "Black rook at h8 is missing")
        self.assertEqual(board_dict['h8']['type'], 'r', "Piece at h8 should be a rook")
        self.assertEqual(board_dict['h8']['color'], 'black', "Piece at h8 should be black")
        
        self.assertIn('h7', board_dict, "Black pawn at h7 is missing")
        self.assertEqual(board_dict['h7']['type'], 'p', "Piece at h7 should be a pawn")
        self.assertEqual(board_dict['h7']['color'], 'black', "Piece at h7 should be black")
        
        # Check for white pieces
        white_pieces = [f"{f}{r}" for f in "abcdefgh" for r in "12"]
        for square in white_pieces:
            self.assertIn(square, board_dict, f"White piece at {square} is missing")
            self.assertEqual(board_dict[square]['color'], 'white', f"Piece at {square} should be white")
    
    def test_api_initialize_returns_complete_board(self):
        """Test that the /initialize endpoint returns a complete board with all pieces."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                               data='{"difficulty": "medium"}',
                               content_type='application/json')
        
        self.assertEqual(init_response.status_code, 200, "Initialize request should succeed")
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Verify we have all 32 pieces
        self.assertEqual(len(init_board), 32, "API should return board with exactly 32 pieces")
        
        # Specifically check for previously missing pieces
        self.assertIn('h8', init_board, "Black rook at h8 is missing from API response")
        self.assertEqual(init_board['h8']['type'], 'r', "Piece at h8 should be a rook")
        self.assertEqual(init_board['h8']['color'], 'black', "Piece at h8 should be black")
        
        self.assertIn('h7', init_board, "Black pawn at h7 is missing from API response")
        self.assertEqual(init_board['h7']['type'], 'p', "Piece at h7 should be a pawn")
        self.assertEqual(init_board['h7']['color'], 'black', "Piece at h7 should be black")
        
        # Check for white pieces
        white_squares = [
            'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1',  # Back rank
            'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'   # Pawns
        ]
        
        for square in white_squares:
            self.assertIn(square, init_board, f"White piece at {square} is missing from API response")
            self.assertEqual(init_board[square]['color'], 'white', f"Piece at {square} should be white") 