import unittest
import json
import sys
import os
import logging

# Add the parent directory to the path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, square_to_coord, coord_to_square
import app as app_module  # Import the module to access global variables

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestFrontendMoveInteraction(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app for each test."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_key'  # Required for sessions
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Initialize a new game and store the response
        response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        self.init_data = response.get_json()
        logger.debug(f"Initialize response: {self.init_data}")
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def verify_piece_at_position(self, square, expected_piece=None, expected_color=None):
        """Verify if a piece exists at the given square with expected properties."""
        # Get the current board state
        with self.client.session_transaction() as sess:
            logger.debug(f"Session contents: {sess}")
            
        # Make a move request to get the updated board state
        resp = self.client.post('/move', 
                              data=json.dumps({"from": "a1", "to": "a1"}),  # No-op move just to get state
                              content_type='application/json')
        board_data = resp.get_json()
        
        logger.debug(f"Board data: {board_data}")
        
        if expected_piece is None:
            # Should not have a piece
            self.assertNotIn(square, board_data.get('board', {}), f"No piece should be at {square}")
            return True
            
        # Should have a piece with expected properties
        self.assertIn(square, board_data.get('board', {}), f"Piece should be at {square}")
        piece = board_data.get('board', {}).get(square, {})
        
        if expected_piece:
            piece_type = piece.get('type')
            self.assertIn(piece_type, [expected_piece, expected_piece[0]], 
                         f"Piece at {square} should be a {expected_piece}, got {piece_type}")
            
        if expected_color:
            self.assertEqual(piece.get('color'), expected_color, 
                           f"Piece at {square} should be {expected_color}")
        
        return True
    
    def test_pawn_movement_e2_to_e4(self):
        """Test specific pawn movement from e2 to e4 and debug the process."""
        # Verify initial state
        self.verify_piece_at_position('e2', 'pawn', 'white')
        self.verify_piece_at_position('e4', None)
        
        # Make the move
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e2", "to": "e4"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        logger.debug(f"Move response: {move_data}")
        
        # Debug the internal state of current_position
        with app.app_context():
            board_state = app_module.current_position.board if app_module.current_position else None
            logger.debug(f"Current position board state: {board_state}")
            if app_module.current_position:
                logger.debug(f"Legal moves: {[coord_to_square(m[0])+coord_to_square(m[1]) for m in app_module.current_position.gen_moves()]}")
        
        # Check response has expected structure
        self.assertIn('valid', move_data, "Response should indicate if move is valid")
        self.assertIn('board', move_data, "Response should include board state")
        
        # Verify the move was successful
        self.assertTrue(move_data.get('valid', False), "Move e2-e4 should be valid")
        
        # Verify the piece has moved
        self.verify_piece_at_position('e2', None)
        self.verify_piece_at_position('e4', 'pawn', 'white')
    
    def test_move_with_direct_position_update(self):
        """Test that the Position.move() function correctly updates the internal board.

        The /move route requires a valid 'from'/'to' pair; there is no
        "check_state" shortcut.  This test verifies the Position object's move
        method directly (without the HTTP layer) and then confirms the board is
        correctly reflected when read back through board_to_dict.
        """
        from chess_logic_by_thomasahle import Position
        from app import board_to_dict

        with app.app_context():
            initial_position = app_module.current_position

            e2_coord = square_to_coord('e2')
            e4_coord = square_to_coord('e4')

            legal_moves = list(initial_position.gen_moves())
            move_tuple = (e2_coord, e4_coord)

            e2e4_exists = any(m[0] == e2_coord and m[1] == e4_coord for m in legal_moves)
            self.assertTrue(e2e4_exists, "e2-e4 should be a legal move")

            # Apply the move directly on the Position object.
            # Position.move() always rotates the board so the opponent is next.
            new_position = initial_position.move(move_tuple)
            self.assertIsNotNone(new_position, "Move should return a new position")

            # Rotate back to white's perspective to inspect the resulting board.
            white_perspective = new_position.rotate()

            board_dict = board_to_dict(white_perspective)
            self.assertNotIn('e2', board_dict, "e2 should be empty after the move")
            self.assertIn('e4', board_dict, "e4 should have a piece after the move")
            self.assertEqual(board_dict['e4']['color'], 'white', "Piece at e4 should be white")
            self.assertEqual(board_dict['e4']['type'], 'p', "Piece at e4 should be a pawn")
    
    def test_make_move_endpoint(self):
        """Test the /move endpoint with direct debugging of the app state."""
        # Make a move
        move_response = self.client.post('/move', 
                                       data=json.dumps({"from": "e2", "to": "e4"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        logger.debug(f"Move response: {json.dumps(move_data, indent=2)}")
        
        # Check if move was processed correctly
        self.assertTrue(move_data.get('valid', False), 
                       f"Move should be valid, got response: {move_data}")
        
        # Verify the board state after move
        self.assertIn('board', move_data, "Response should include board state")
        board = move_data.get('board', {})
        
        # Verify piece moved from e2 to e4
        self.assertNotIn('e2', board, "Piece should no longer be at e2")
        self.assertIn('e4', board, "Piece should now be at e4")
        
        # Verify it's the correct piece
        piece = board.get('e4', {})
        self.assertEqual(piece.get('color'), 'white', "Piece should be white")
        self.assertIn(piece.get('type'), ['pawn', 'p'], "Piece should be a pawn")
    
    def test_move_flow_with_debugging(self):
        """Test the complete move flow with detailed debugging."""
        # Get initial board state
        with app.app_context():
            initial_position = app_module.current_position
            logger.debug(f"Initial current_position: {initial_position}")
            
            # Debug the coordinates
            e2_coord = square_to_coord('e2')
            e4_coord = square_to_coord('e4')
            logger.debug(f"e2_coord: {e2_coord}, e4_coord: {e4_coord}")
            
            # Check legal moves
            legal_moves = list(initial_position.gen_moves())
            logger.debug(f"Legal moves: {legal_moves}")
            
            # Check if e2-e4 is in legal moves
            e2e4_in_moves = any(move[0] == e2_coord and move[1] == e4_coord for move in legal_moves)
            logger.debug(f"e2-e4 in legal moves: {e2e4_in_moves}")
        
        # Make the move through the API
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e2", "to": "e4"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        logger.debug(f"Move API response: {json.dumps(move_data, indent=2)}")
        
        # Verify the global state was updated
        with app.app_context():
            new_position = app_module.current_position
            logger.debug(f"New current_position: {new_position}")
            
            # Get piece at e4
            # The board is a string, not a dictionary, so we need to access by index
            e4_piece = new_position.board[e4_coord] if e4_coord < len(new_position.board) else None
            logger.debug(f"Piece at e4: {e4_piece}")
            
            # Get piece at e2 (should be '.')
            e2_piece = new_position.board[e2_coord] if e2_coord < len(new_position.board) else None
            logger.debug(f"Piece at e2: {e2_piece}")
        
        # Final assertions
        self.assertTrue(move_data.get('valid', False), "Move should be valid")
        self.assertNotIn('e2', move_data.get('board', {}), "Piece should have left e2")
        self.assertIn('e4', move_data.get('board', {}), "Piece should now be at e4")

if __name__ == '__main__':
    unittest.main() 