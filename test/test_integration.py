import unittest
import json
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class ChessEngineIntegrationTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app for integration testing."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_complete_game_workflow(self):
        """Test a complete game workflow to verify all fixed issues."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        self.assertEqual(init_data['currentPlayer'], 'white', "Game should start with white player")
        
        # Track piece positions to verify no shifting 
        initial_board = init_data['board']
        self._verify_board_integrity(initial_board)
        self._verify_no_black_text(initial_board)
        
        # Make several moves to verify both issues don't appear
        
        # First move: e2-e4
        first_move_response = self.client.post('/move',
                                   data='{"from": "e2", "to": "e4"}',
                                   content_type='application/json')
        first_move_data = first_move_response.get_json()
        self.assertTrue(first_move_data['valid'], "First move should be valid")
        self.assertEqual(first_move_data['currentPlayer'], 'white', "After AI moves, should be white's turn")
        
        # Verify board integrity after first move
        first_board = first_move_data['board'] 
        self._verify_board_integrity(first_board)
        self._verify_no_black_text(first_board)
        
        # Second move: Knight g1-f3
        second_move_response = self.client.post('/move',
                                   data='{"from": "g1", "to": "f3"}',
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        self.assertTrue(second_move_data['valid'], "Second move should be valid")
        
        # Verify board integrity after second move
        second_board = second_move_data['board']
        self._verify_board_integrity(second_board)
        self._verify_no_black_text(second_board)
        
        # Third move: Bishop f1-c4 (previously problematic move)
        third_move_response = self.client.post('/move',
                                   data='{"from": "f1", "to": "c4"}',
                                   content_type='application/json')
        third_move_data = third_move_response.get_json()
        self.assertTrue(third_move_data['valid'], "Third move should be valid")
        
        # Verify board integrity after third move - this was where shifting happened before
        third_board = third_move_data['board']
        self._verify_board_integrity(third_board)
        self._verify_no_black_text(third_board)
        
        # Verify the third move pieces are in expected positions
        self.assertIn('c4', third_board, "Bishop should be at c4")
        self.assertEqual(third_board['c4']['type'], 'b', "c4 should contain a bishop")
        self.assertEqual(third_board['c4']['color'], 'white', "Bishop should be white")
        
        # Verify turn handling - try to make a move when it's not the player's turn
        # Set up a special test case where we force black's turn
        invalid_turn_response = self.client.post('/move',
                                   data='{"from": "d1", "to": "f3", "_forceBlackTurn": true}',
                                   content_type='application/json')
        invalid_turn_data = invalid_turn_response.get_json()
        
        # Verify it was rejected
        self.assertFalse(invalid_turn_data['valid'], "Move should be rejected when not player's turn")
        self.assertIn("Not your turn", invalid_turn_data['message'], "Error message should indicate wrong turn")
        
    def _verify_board_integrity(self, board):
        """Verify the integrity of the chess board data structure."""
        # Verify we have the right number of pieces
        # In a standard chess board after some moves, we should have around 30-32 pieces
        self.assertTrue(len(board) >= 28, f"Board should have at least 28 pieces, but has {len(board)}")
        
        # Verify each piece has the expected properties
        for square, piece in board.items():
            # Verify square notation
            self.assertTrue(len(square) == 2, f"Square notation should be 2 chars: {square}")
            self.assertTrue(square[0] in 'abcdefgh', f"File should be a-h: {square}")
            self.assertTrue(square[1] in '12345678', f"Rank should be 1-8: {square}")
            
            # Verify piece has required properties
            self.assertIn('type', piece, f"Piece at {square} should have 'type'")
            self.assertIn('color', piece, f"Piece at {square} should have 'color'")
            
            # Verify property values
            self.assertIn(piece['type'], ['p', 'r', 'n', 'b', 'q', 'k'], 
                         f"Piece type should be valid: {piece['type']}")
            self.assertIn(piece['color'], ['white', 'black'], 
                         f"Piece color should be 'white' or 'black': {piece['color']}")
        
    def _verify_no_black_text(self, board):
        """Verify there's no raw 'black' text in the wrong places."""
        for square, piece in board.items():
            is_black_piece = piece['color'] == 'black'
            
            # Convert to JSON to check for raw "black" text
            piece_json = json.dumps(piece)
            
            if is_black_piece:
                # For black pieces, "black" should only appear once (as the color value)
                self.assertEqual(piece_json.lower().count('black'), 1, 
                               f"Black piece at {square} should only have 'black' once: {piece}")
            else:
                # For non-black pieces, "black" should not appear at all
                self.assertNotIn('black', piece_json.lower(), 
                               f"Non-black piece at {square} should not have 'black': {piece}")

if __name__ == '__main__':
    unittest.main() 