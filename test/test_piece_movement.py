import unittest
import json
from flask import url_for
from app import app, board_to_dict, current_position
from chess_logic_by_thomasahle import Position, initial

class ChessPieceMovementTestCase(unittest.TestCase):
    
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
    
    def test_move_backend_processing(self):
        """Test that the backend properly processes moves and updates the board state."""
        # Make a valid pawn move from e2 to e4
        move_response = self.client.post('/move',
                                     data=json.dumps({"from": "e2", "to": "e4"}),
                                     content_type='application/json')
        move_data = move_response.get_json()
        
        # Test that the move was considered valid
        self.assertTrue(move_data['valid'], "Valid move should be accepted")
        
        # Test that the board state has been updated
        self.assertIn('e4', move_data['board'], "Pawn should now be at e4")
        self.assertNotIn('e2', move_data['board'], "Pawn should no longer be at e2")
        
        # Check the piece attributes at the new position
        piece = move_data['board']['e4']
        self.assertEqual(piece['type'], 'pawn', "Piece should be a pawn")
        self.assertEqual(piece['color'], 'white', "Piece should be white")
        
        # Test that the current player has changed to white after the AI makes its move
        self.assertEqual(move_data['currentPlayer'], 'white', "After white's move and AI's response, it should be white's turn again")
        
        # Check that the move is recorded in the move history
        self.assertTrue(any(move['from'] == 'e2' and move['to'] == 'e4' for move in move_data['moves']),
                      "Move should be recorded in the move history")
    
    def test_invalid_move_rejected(self):
        """Test that invalid moves are properly rejected."""
        # Try to make an invalid move (moving a pawn 3 squares)
        move_response = self.client.post('/move',
                                     data=json.dumps({"from": "e2", "to": "e5"}),
                                     content_type='application/json')
        move_data = move_response.get_json()
        
        # Test that the move was rejected
        self.assertFalse(move_data['valid'], "Invalid move should be rejected")
        
        # Test that the board state remains unchanged
        self.assertIn('e2', move_data['board'], "Pawn should still be at e2")
        self.assertNotIn('e5', move_data['board'], "No piece should be at e5")
        
        # Test that the current player hasn't changed
        self.assertEqual(move_data['currentPlayer'], 'white', "After rejected move, it should still be white's turn")
    
    def test_move_sequence(self):
        """Test a sequence of moves to ensure proper board state tracking."""
        # Move 1: White pawn e2-e4
        move1_response = self.client.post('/move',
                                     data=json.dumps({"from": "e2", "to": "e4"}),
                                     content_type='application/json')
        move1_data = move1_response.get_json()
        self.assertTrue(move1_data['valid'], "First move should be valid")
        
        # Get AI's move from the response
        ai_move = move1_data.get('aiMove', {})
        self.assertIsNotNone(ai_move, "AI should make a move in response")
        ai_from = ai_move.get('from')
        ai_to = ai_move.get('to')
        
        # Move 2: Another white move after AI's move
        move2_response = self.client.post('/move',
                                     data=json.dumps({"from": "d2", "to": "d4"}),
                                     content_type='application/json')
        move2_data = move2_response.get_json()
        self.assertTrue(move2_data['valid'], "Second move should be valid")
        
        # Verify the board state after two moves
        board = move2_data['board']
        self.assertIn('e4', board, "Pawn from first move should be at e4")
        self.assertIn('d4', board, "Pawn from second move should be at d4")
        self.assertNotIn('e2', board, "No pawn should remain at e2")
        self.assertNotIn('d2', board, "No pawn should remain at d2")
        
        # Verify both moves are in the move history
        moves = move2_data['moves']
        move_strings = [f"{m['from']}-{m['to']}" for m in moves]
        self.assertIn("e2-e4", move_strings, "First move should be in history")
        self.assertIn("d2-d4", move_strings, "Second move should be in history")
        
        # Verify AI move is also recorded in history
        ai_move_string = f"{ai_from}-{ai_to}"
        self.assertIn(ai_move_string, move_strings, "AI's move should be in history")
    
    def test_frontend_api_integration(self):
        """Test that the API endpoints needed by the frontend work correctly."""
        # Initialize a new game
        init_response = self.client.post('/initialize',
                                     data=json.dumps({"difficulty": "easy"}),
                                     content_type='application/json')
        init_data = init_response.get_json()
        
        # Verify the API structure matches what the frontend expects
        self.assertIn('board', init_data, "API should return a board state")
        self.assertIn('gameState', init_data, "API should return the game state")
        self.assertIn('currentPlayer', init_data, "API should return the current player")
        
        # Make a move
        move_response = self.client.post('/move',
                                     data=json.dumps({"from": "e2", "to": "e4"}),
                                     content_type='application/json')
        move_data = move_response.get_json()
        
        # Check that the move response has all needed fields for frontend
        self.assertIn('valid', move_data, "API should indicate if move is valid")
        self.assertIn('board', move_data, "API should return updated board")
        self.assertIn('moves', move_data, "API should return move history")
        self.assertIn('currentPlayer', move_data, "API should return current player")
        
        # If the move was successful, there should be an AI move as well
        if move_data['valid']:
            self.assertIn('aiMove', move_data, "API should return AI's move")
            if move_data['aiMove']:
                self.assertIn('from', move_data['aiMove'], "AI move should have 'from' coordinate")
                self.assertIn('to', move_data['aiMove'], "AI move should have 'to' coordinate")
    
    def test_move_handler_function(self):
        """Test the make_move function directly to ensure it validates and processes moves correctly."""
        from app import make_move
        
        # Manually create a test client to test the route function
        with app.test_request_context(json={"from": "e2", "to": "e4"}):
            # Call the function directly
            response = make_move()
            data = json.loads(response.get_data(as_text=True))
            
            # Verify the move was processed correctly
            self.assertTrue(data['valid'], "Valid move should be accepted")
            self.assertIn('e4', data['board'], "Board should be updated with new position")
            self.assertNotIn('e2', data['board'], "Old position should be empty")

if __name__ == '__main__':
    unittest.main() 