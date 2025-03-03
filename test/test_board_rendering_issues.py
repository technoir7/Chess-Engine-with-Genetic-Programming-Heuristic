import unittest
import json
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class BoardRenderingIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_no_black_text_on_board(self):
        """Test that there's no 'black' text appearing incorrectly on the board."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Check that no raw "black" text appears where it shouldn't
        self._check_no_raw_black_text(init_board)
        
        # Now make moves to get to the third move where issues appear
        # First move (e2-e4)
        first_move_response = self.client.post('/move',
                                   data='{"from": "e2", "to": "e4"}',
                                   content_type='application/json')
        first_move_data = first_move_response.get_json()
        first_board = first_move_data['board']
        
        # Check after first move
        self._check_no_raw_black_text(first_board)
        
        # Second move (knight to f3)
        second_move_response = self.client.post('/move',
                                   data='{"from": "g1", "to": "f3"}',
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        second_board = second_move_data['board']
        
        # Check after second move
        self._check_no_raw_black_text(second_board)
        
        # Third move (bishop to c4) - this is where issues typically appear
        third_move_response = self.client.post('/move',
                                   data='{"from": "f1", "to": "c4"}',
                                   content_type='application/json')
        third_move_data = third_move_response.get_json()
        third_board = third_move_data['board']
        
        # Check specifically for issues on the 8th rank and h file
        self._check_no_raw_black_text(third_board)
        self._check_eighth_rank_and_h_file(third_board)
        
    def test_no_board_shifting(self):
        """Test that the board doesn't shift down and left after the third move."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Track the initial positions of some key pieces that should remain stationary
        initial_positions = self._get_piece_positions(init_board)
        
        # First move (e2-e4)
        first_move_response = self.client.post('/move',
                                   data='{"from": "e2", "to": "e4"}',
                                   content_type='application/json')
        first_move_data = first_move_response.get_json()
        first_board = first_move_data['board']
        
        # Track positions after first move
        first_move_positions = self._get_piece_positions(first_board)
        self._assert_stationary_pieces_unchanged(initial_positions, first_move_positions)
        
        # Second move (knight to f3)
        second_move_response = self.client.post('/move',
                                   data='{"from": "g1", "to": "f3"}',
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        second_board = second_move_data['board']
        
        # Track positions after second move
        second_move_positions = self._get_piece_positions(second_board)
        self._assert_stationary_pieces_unchanged(initial_positions, second_move_positions)
        
        # Third move (bishop to c4) - this is where shifting issues typically appear
        third_move_response = self.client.post('/move',
                                   data='{"from": "f1", "to": "c4"}',
                                   content_type='application/json')
        third_move_data = third_move_response.get_json()
        third_board = third_move_data['board']
        
        # Track positions after third move
        third_move_positions = self._get_piece_positions(third_board)
        
        # Verify no shifting has occurred for stationary pieces
        self._assert_stationary_pieces_unchanged(initial_positions, third_move_positions)
        
        # Additionally verify specific moved pieces are in their correct positions
        self.assertIn('e4', third_board, "Pawn should be at e4")
        self.assertEqual(third_board['e4']['type'], 'p', "Piece at e4 should be a pawn")
        self.assertEqual(third_board['e4']['color'], 'white', "Pawn at e4 should be white")
        
        self.assertIn('f3', third_board, "Knight should be at f3")
        self.assertEqual(third_board['f3']['type'], 'n', "Piece at f3 should be a knight")
        self.assertEqual(third_board['f3']['color'], 'white', "Knight at f3 should be white")
        
        self.assertIn('c4', third_board, "Bishop should be at c4")
        self.assertEqual(third_board['c4']['type'], 'b', "Piece at c4 should be a bishop")
        self.assertEqual(third_board['c4']['color'], 'white', "Bishop at c4 should be white")
    
    def test_board_to_dict_parsing(self):
        """Test the board_to_dict function directly to ensure proper parsing."""
        # Create a new test position
        test_position = Position(initial, 0, (True,True), (True,True), 0, 0)
        
        # Generate the board dictionary
        board_dict = board_to_dict(test_position)
        
        # Normalize the board to remove 'code' property if present
        normalized_board = self._normalize_pieces(board_dict)
        
        # Verify the dictionary has the correct number of pieces
        self.assertEqual(len(normalized_board), 32, "Board should have 32 pieces total")
        
        # Check that no raw "black" text appears incorrectly
        self._check_no_raw_black_text(normalized_board)
        
        # Check specific pieces on the 8th rank and h file
        self._check_eighth_rank_and_h_file(normalized_board)
        
        # Verify no pieces have invalid properties or values
        for square, piece in normalized_board.items():
            # Check pieces have only the expected properties
            self.assertIn('type', piece, f"Piece at {square} missing 'type' property")
            self.assertIn('color', piece, f"Piece at {square} missing 'color' property") 
            
            # Check type and color have valid values
            self.assertIn(piece['type'], ['p', 'r', 'n', 'b', 'q', 'k'], 
                         f"Piece at {square} has invalid type: {piece['type']}")
            self.assertIn(piece['color'], ['white', 'black'], 
                         f"Piece at {square} has invalid color: {piece['color']}")
            
            # Ensure no extraneous properties
            self.assertEqual(len(piece), 2, f"Piece at {square} has extra properties: {piece}")
    
    def _check_no_raw_black_text(self, board):
        """Helper method to check that no raw 'black' text appears in the wrong place."""
        # Normalize pieces (remove 'code' property if present)
        normalized_board = self._normalize_pieces(board)
        
        # Check through all pieces
        for square, piece in normalized_board.items():
            # Check if this is a black piece
            is_black_piece = piece['color'] == 'black'
            
            # For pieces that aren't black, 'black' should never appear in any property
            if not is_black_piece:
                piece_json = json.dumps(piece)
                self.assertNotIn('black', piece_json.lower(), 
                              f"Found 'black' text in non-black piece at {square}: {piece}")
            
            # For black pieces, 'black' should only appear as the value of the 'color' property
            if is_black_piece:
                # Convert to JSON and count occurrences of "black"
                piece_json = json.dumps(piece)
                occurrences = piece_json.lower().count('black')
                self.assertEqual(occurrences, 1, 
                               f"Found multiple instances of 'black' in piece at {square}: {piece}")
    
    def _normalize_pieces(self, board):
        """Helper method to normalize piece representation by removing 'code' property if present."""
        normalized_board = {}
        for square, piece in board.items():
            normalized_piece = piece.copy()  # Make a copy to avoid modifying the original
            if 'code' in normalized_piece:
                del normalized_piece['code']  # Remove 'code' property if present
            normalized_board[square] = normalized_piece
        return normalized_board
    
    def _check_eighth_rank_and_h_file(self, board):
        """Helper method to specifically check the 8th rank and h file for issues."""
        # Normalize pieces (remove 'code' property if present)
        normalized_board = self._normalize_pieces(board)
        
        # Check 8th rank pieces (a8-h8)
        for file_char in 'abcdefgh':
            square = f"{file_char}8"
            if square in normalized_board:
                piece = normalized_board[square]
                # Verify no extra properties
                self.assertEqual(len(piece), 2, f"Piece at {square} has extra properties: {piece}")
                # Verify no raw "black" text besides color property if it's a black piece
                if piece['color'] == 'black':
                    piece_json = json.dumps(piece)
                    self.assertEqual(piece_json.lower().count('black'), 1, 
                                    f"Found multiple instances of 'black' in 8th rank piece at {square}")
        
        # Check h file pieces (h1-h8)
        for rank in range(1, 9):
            square = f"h{rank}"
            if square in normalized_board:
                piece = normalized_board[square]
                # Verify no extra properties
                self.assertEqual(len(piece), 2, f"Piece at {square} has extra properties: {piece}")
                # Verify no raw "black" text besides color property if it's a black piece
                if piece['color'] == 'black':
                    piece_json = json.dumps(piece)
                    self.assertEqual(piece_json.lower().count('black'), 1, 
                                    f"Found multiple instances of 'black' in h file piece at {square}")
    
    def _get_piece_positions(self, board):
        """Helper method to track positions of stationary pieces for shift detection."""
        # Track pieces that shouldn't move during our test sequence
        stationary_pieces = {
            'a1': board.get('a1'),  # white rook
            'e1': board.get('e1'),  # white king
            'd1': board.get('d1'),  # white queen
            'a7': board.get('a7'),  # black pawn
            'e8': board.get('e8'),  # black king
        }
        return stationary_pieces
    
    def _assert_stationary_pieces_unchanged(self, original_positions, current_positions):
        """Helper method to verify stationary pieces haven't moved (no shifting)."""
        for square, piece in original_positions.items():
            if piece:  # Only check if the piece existed originally
                self.assertIn(square, current_positions, f"Piece at {square} is missing")
                current_piece = current_positions[square]
                if current_piece:
                    self.assertEqual(piece['type'], current_piece['type'], 
                                   f"Piece type at {square} changed from {piece['type']} to {current_piece['type']}")
                    self.assertEqual(piece['color'], current_piece['color'], 
                                   f"Piece color at {square} changed from {piece['color']} to {current_piece['color']}")

if __name__ == '__main__':
    unittest.main() 