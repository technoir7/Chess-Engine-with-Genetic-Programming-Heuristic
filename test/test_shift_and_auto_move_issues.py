import unittest
from app import app
from chess_logic_by_thomasahle import Position, initial
import json

class ShiftAndAutoMoveIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_no_piece_shift_on_third_move(self):
        """Test that pieces don't shift down and left on the third move with 'black' text appearing."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        # Track piece locations before moves
        init_data = init_response.get_json()
        initial_board = init_data['board']
        
        # Make first move (e2-e4)
        first_move_response = self.client.post('/move',
                                   data='{"from": "e2", "to": "e4"}',
                                   content_type='application/json')
        first_move_data = first_move_response.get_json()
        
        # AI makes a move in response
        ai_move_from = first_move_data['aiMove']['from']
        ai_move_to = first_move_data['aiMove']['to']
        first_board_after = first_move_data['board']
        
        # Make second move (knight to f3)
        second_move_response = self.client.post('/move',
                                   data='{"from": "g1", "to": "f3"}',
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        
        # AI makes another move in response
        second_ai_move_from = second_move_data['aiMove']['from']
        second_ai_move_to = second_move_data['aiMove']['to']
        second_board_after = second_move_data['board']
        
        # Make third move (bishop to c4)
        third_move_response = self.client.post('/move',
                                   data='{"from": "f1", "to": "c4"}',
                                   content_type='application/json')
        third_move_data = third_move_response.get_json()
        third_board_after = third_move_data['board']
        
        # Check that white pieces are still in expected locations after third move
        # These are pieces that haven't moved yet (should be in original positions)
        expected_positions = {
            'a1': {'type': 'r', 'color': 'white'},
            'b1': {'type': 'n', 'color': 'white'},
            'c1': {'type': 'b', 'color': 'white'},
            'd1': {'type': 'q', 'color': 'white'},
            'e1': {'type': 'k', 'color': 'white'},
            'h1': {'type': 'r', 'color': 'white'},
        }
        
        for square, expected_piece in expected_positions.items():
            self.assertIn(square, third_board_after, f"Piece should be at {square} after third move")
            actual_piece = third_board_after[square]
            self.assertEqual(actual_piece['type'], expected_piece['type'], 
                             f"Piece at {square} should be a {expected_piece['type']}")
            self.assertEqual(actual_piece['color'], expected_piece['color'], 
                             f"Piece at {square} should be {expected_piece['color']}")
            
        # Check that moved pieces are in their new expected positions
        self.assertIn('e4', third_board_after, "Pawn should be at e4")
        self.assertEqual(third_board_after['e4']['type'], 'p')
        self.assertEqual(third_board_after['e4']['color'], 'white')
        
        self.assertIn('f3', third_board_after, "Knight should be at f3")
        self.assertEqual(third_board_after['f3']['type'], 'n')
        self.assertEqual(third_board_after['f3']['color'], 'white')
        
        self.assertIn('c4', third_board_after, "Bishop should be at c4")
        self.assertEqual(third_board_after['c4']['type'], 'b')
        self.assertEqual(third_board_after['c4']['color'], 'white')
        
        # Check there's no "black" text on the board
        # This is done by ensuring there are no unexpected properties in pieces
        allowed_properties = ['type', 'color']
        
        for square, piece in third_board_after.items():
            # Check each piece has only the expected properties
            for prop in piece:
                self.assertIn(prop, allowed_properties, 
                              f"Unexpected property '{prop}' found in piece at {square}")
            
            # Check no literals of "black" appearing incorrectly
            if piece['color'] != 'black':
                for value in piece.values():
                    self.assertNotIn('black', str(value).lower(), 
                                     f"'black' text found in piece at {square}")
    
    def test_engine_not_making_player_moves(self):
        """Test that the engine does not make moves for the player."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                  data='{"difficulty": "easy"}',
                                  content_type='application/json')
        init_data = init_response.get_json()
        initial_board = init_data['board']
        
        # Check if currentPlayer is included in the response
        self.assertIn('currentPlayer', init_data, "Response should include currentPlayer field")
        self.assertEqual(init_data.get('currentPlayer'), 'white', "Game should start with player's turn")
        
        # Make first move (e2-e4)
        first_move_response = self.client.post('/move',
                                   data='{"from": "e2", "to": "e4"}',
                                   content_type='application/json')
        first_move_data = first_move_response.get_json()
        
        # Check if currentPlayer is updated in the response
        self.assertIn('currentPlayer', first_move_data, "Response should include currentPlayer field")
        self.assertEqual(first_move_data.get('currentPlayer'), 'white', 
                         "After AI's move, it should be player's turn again")
        
        # Make second player move
        second_move_response = self.client.post('/move',
                                   data='{"from": "g1", "to": "f3"}',
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        
        # Check currentPlayer again
        self.assertIn('currentPlayer', second_move_data, "Response should include currentPlayer field")
        self.assertEqual(second_move_data.get('currentPlayer'), 'white',
                         "After AI's second move, it should be player's turn again")
        
        # THIS IS WHERE THE TEST WILL SIMULATE THE BUG:
        # Now we want to test what happens when the backend thinks it's the AI's turn
        # We'll manually set the current_player to 'black' to simulate this scenario
        invalid_turn_response = self.client.post('/move',
                                   data='{"from": "b1", "to": "c3", "_forceBlackTurn": true}',
                                   content_type='application/json')
        invalid_turn_data = invalid_turn_response.get_json()
        
        # Print detailed information for debugging
        print("\nDETAILED TEST FAILURE INFORMATION:")
        print(f"Response from invalid turn move: {invalid_turn_data}")
        print(f"Valid flag: {invalid_turn_data.get('valid')}")
        print(f"Message: {invalid_turn_data.get('message')}")
        print(f"Current player in response: {invalid_turn_data.get('currentPlayer')}")
        
        # We should not accept this move, since we're forcing it to be during AI's turn
        self.assertFalse(invalid_turn_data.get('valid', True), 
                         "Moves should be rejected when it's not player's turn")

if __name__ == '__main__':
    unittest.main() 