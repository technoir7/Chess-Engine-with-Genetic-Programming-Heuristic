import unittest
import json
import sys
import os

# Add the parent directory to the path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, board_to_dict, square_to_coord, coord_to_square
from chess_logic_by_thomasahle import Position, initial

class TestPieceMovementIssues(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Initialize a new game before each test
        response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        self.init_data = response.get_json()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_move_flow_debug(self):
        """Debug test that examines the entire move flow step by step.

        board_to_dict returns single-letter type codes ('p' not 'pawn').
        """
        print("Initial board state:")
        initial_board = self.init_data.get('board', {})
        self.assertIn('e2', initial_board, "Initial board should have a piece at e2")
        piece_at_e2 = initial_board.get('e2', {})
        self.assertEqual(piece_at_e2.get('type'), 'p', "Piece at e2 should be a pawn (type='p')")
        self.assertEqual(piece_at_e2.get('color'), 'white', "Piece at e2 should be white")
        
        # 2. Print internal board representation
        from app import current_position
        print("\nInternal board representation:")
        print(current_position.board)
        
        # 3. Generate valid moves and print them
        print("\nValid moves from current position:")
        valid_moves = list(current_position.gen_moves())
        print(f"Number of valid moves: {len(valid_moves)}")
        valid_algebraic_moves = [(coord_to_square(m[0]), coord_to_square(m[1])) for m in valid_moves]
        print(f"First 5 valid moves: {valid_algebraic_moves[:5]}")
        
        # 4. Check if e2-e4 is in valid moves
        move_e2_e4 = (square_to_coord('e2'), square_to_coord('e4'))
        self.assertIn(move_e2_e4, valid_moves, "e2-e4 should be a valid move")
        
        # 5. Attempt to make the move through the API
        print("\nAttempting to make move e2-e4:")
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e2", "to": "e4"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        print(f"Move response: {move_data.get('valid', False)}")
        
        # Check response
        if 'error' in move_data:
            print(f"Error: {move_data['error']}")
        
        # 6. Verify the move was successful
        self.assertTrue('valid' in move_data, "Response should include 'valid' field")
        if 'valid' in move_data:
            self.assertTrue(move_data['valid'], "Move should be valid")
        
        # 7. Check the updated board state
        updated_board = move_data.get('board', {})
        self.assertIn('e4', updated_board, "Updated board should have a piece at e4")
        self.assertNotIn('e2', updated_board, "Updated board should not have a piece at e2")
        
        # 8. Verify AI move happened
        self.assertIn('aiMove', move_data, "AI should have made a move")
        ai_move = move_data.get('aiMove', {})
        self.assertIsNotNone(ai_move, "AI move should not be None")
        print(f"\nAI move: {ai_move}")
    
    def test_move_function_directly(self):
        """Test the Position.move function directly."""
        # Get current position from app context
        from app import current_position
        
        # Manually execute a move
        e2 = square_to_coord('e2')
        e4 = square_to_coord('e4')
        move = (e2, e4)
        
        # This should produce a new position with the pawn moved
        new_position = current_position.move(move)
        
        # The position is rotated after a move, so rotate it back for comparison
        new_position = new_position.rotate()
        
        # Check that e2 is now empty and e4 has a pawn
        self.assertEqual(new_position.board[e4], 'P', "After move, e4 should contain a pawn")
        self.assertEqual(new_position.board[e2], '.', "After move, e2 should be empty")
    
    def test_coordinate_transformations(self):
        """Test that coordinate transformations work correctly."""
        # Test square_to_coord
        self.assertEqual(square_to_coord('a1'), 91, "a1 should map to internal coordinate 91")
        self.assertEqual(square_to_coord('h8'), 28, "h8 should map to internal coordinate 28")
        self.assertEqual(square_to_coord('e2'), 85, "e2 should map to internal coordinate 85")
        
        # Test coord_to_square
        self.assertEqual(coord_to_square(91), 'a1', "Internal coordinate 91 should map to a1")
        self.assertEqual(coord_to_square(28), 'h8', "Internal coordinate 28 should map to h8")
        self.assertEqual(coord_to_square(85), 'e2', "Internal coordinate 85 should map to e2")
        
        # Test a round trip
        squares = ['a1', 'h8', 'e2', 'e4', 'd5', 'g1']
        for square in squares:
            self.assertEqual(coord_to_square(square_to_coord(square)), square, 
                          f"Round trip conversion of {square} should return the same square")
    
    def test_move_handler_request_processing(self):
        """Test how the move handler processes requests."""
        # Make a move request
        move_request = {"from": "e2", "to": "e4"}
        
        with app.test_request_context(
            json=move_request,
            method='POST',
            path='/move'
        ):
            # Import the make_move function
            from app import make_move
            
            # Call it directly
            response = make_move()
            
            # Check if it returns a valid response
            self.assertEqual(response.status_code, 200, "Response status should be 200 OK")
            
            # Parse the JSON response
            data = json.loads(response.get_data(as_text=True))
            
            # Verify the move was processed
            self.assertTrue(data.get('valid', False), "Move should be valid")
            
            # Check the board state
            board = data.get('board', {})
            self.assertIn('e4', board, "Board should have a piece at e4")
            self.assertNotIn('e2', board, "Board should not have a piece at e2")

if __name__ == '__main__':
    unittest.main() 