import unittest
import sys
import os
import json
# Add the parent directory to the path so we can import the main application files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chess_logic_by_thomasahle import Position, initial, MATE_LOWER, MATE_UPPER
from minimax import Minimax
from genetic_programming import makerandomtree
import app

class TestEngineResponse(unittest.TestCase):
    def setUp(self):
        # Initialize the chess position
        self.position = Position(initial, 0, (True, True), (True, True), 0, 0)
        # Create a heuristic for the AI
        self.heuristic = makerandomtree(3, self.position)
        # Initialize the searcher
        self.searcher = Minimax(self.heuristic)
        
        # Set up the Flask app for testing
        app.app.config['TESTING'] = True
        self.app_client = app.app.test_client()
        
        # Initialize game globals
        app.current_position = self.position
        app.heuristic = self.heuristic
        app.searcher = self.searcher
        app.move_history = []
        app.current_player = 'white'
        
    def test_engine_response_after_first_move(self):
        """Test that the engine responds after the player's first move."""
        # Get all legal moves for the starting position
        valid_moves = list(self.position.gen_moves())
        self.assertTrue(len(valid_moves) > 0, "No valid moves available from the initial position")
        
        # Choose a sample player move (e.g., e2 to e4)
        # In the internal representation, this might be something like (52, 36)
        sample_move = None
        for move in valid_moves:
            sample_move = move
            break
        
        # Execute the player's move
        new_position = self.position.move(sample_move)
        
        # Try to get a move from the AI
        ai_move_result = self.searcher.search(new_position, secs=1.5)
        
        # The search result should be a tuple (move, score)
        self.assertIsInstance(ai_move_result, tuple, "AI move result should be a tuple (move, score)")
        ai_move, ai_score = ai_move_result
        
        # Verify that AI move is valid
        self.assertIsNotNone(ai_move, "AI move should not be None")
        
        # Check that the AI move is a tuple of two integers (from_coord, to_coord)
        self.assertIsInstance(ai_move, tuple, "AI move should be a tuple (from_coord, to_coord)")
        self.assertEqual(len(ai_move), 2, "AI move should have exactly two elements")
        self.assertIsInstance(ai_move[0], int, "from_coord should be an integer")
        self.assertIsInstance(ai_move[1], int, "to_coord should be an integer")
        
        # Generate all valid moves for the AI's position
        valid_ai_moves = list(new_position.gen_moves())
        
        # Check that the AI's move is in the list of valid moves
        self.assertIn(ai_move, valid_ai_moves, "AI move should be in the list of valid moves")
        
    def test_solution_method(self):
        """Test that the solution method in Minimax returns a valid move."""
        # Get a basic position after one move
        valid_moves = list(self.position.gen_moves())
        sample_move = valid_moves[0]
        new_position = self.position.move(sample_move)
        
        # Call the solution method directly
        solution_result = self.searcher.solution(new_position)
        
        # Verify the result is a tuple (move, score)
        self.assertIsInstance(solution_result, tuple, "Solution result should be a tuple (move, score)")
        self.assertEqual(len(solution_result), 2, "Solution result should have exactly two elements")
        
        move, score = solution_result
        # Check that the move is a tuple (from_coord, to_coord)
        self.assertIsInstance(move, tuple, "Move should be a tuple (from_coord, to_coord)")
        self.assertEqual(len(move), 2, "Move should have exactly two elements")
        
        # Check that the move is valid
        valid_ai_moves = list(new_position.gen_moves())
        self.assertIn(move, valid_ai_moves, "Move should be in the list of valid moves")
        
    def test_make_move_endpoint(self):
        """Test the /move endpoint in the app."""
        # First initialize the game
        init_response = self.app_client.post('/initialize', 
                                           json={'difficulty': 'medium'})
        init_data = json.loads(init_response.data)
        self.assertEqual(init_response.status_code, 200)
        self.assertEqual(init_data['currentPlayer'], 'white')
        
        # Find a valid move from e2 to e4 (standard opening)
        # Convert to internal representation (square to coord)
        from_square = 'e2'
        to_square = 'e4'
        
        # Make the move
        move_response = self.app_client.post('/move', 
                                           json={'from': from_square, 'to': to_square})
        
        # Check that the response is valid
        self.assertEqual(move_response.status_code, 200)
        move_data = json.loads(move_response.data)
        
        # Verify the response contains the AI's move
        self.assertTrue(move_data['valid'])
        self.assertIn('aiMove', move_data)
        self.assertIn('from', move_data['aiMove'])
        self.assertIn('to', move_data['aiMove'])
        
        # Verify move history was updated
        self.assertEqual(len(move_data['moves']), 2)
        self.assertEqual(move_data['moves'][0]['player'], 'white')
        self.assertEqual(move_data['moves'][1]['player'], 'black')
        
        # Verify that the current player is set back to white
        self.assertEqual(app.current_player, 'white')

if __name__ == '__main__':
    unittest.main() 