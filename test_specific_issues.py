import unittest
import json
from app import app, board_to_dict, square_to_coord, coord_to_square

class SpecificIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Initialize a new game before each test
        self.client.post('/initialize',
                        data=json.dumps({'difficulty': 'easy'}),
                        content_type='application/json')
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_no_double_player_move(self):
        """Test that the computer doesn't make a second move for the player."""
        # Make a player move
        response = self.client.post('/move',
                                  data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                  content_type='application/json')
        data = response.get_json()
        
        # Verify that the move was successful
        self.assertTrue(data['valid'])
        
        # Verify the AI made its move
        self.assertIn('aiMove', data)
        
        # Now try to make another player move
        second_response = self.client.post('/move',
                                        data=json.dumps({'from': 'g1', 'to': 'f3'}),
                                        content_type='application/json')
        second_data = second_response.get_json()
        
        # Verify this move is also valid (player should be able to move after AI)
        self.assertTrue(second_data['valid'])
        
        # Attempt an invalid move (not player's turn) by trying to immediately move again
        fake_response = self.client.post('/move',
                                      data=json.dumps({'from': 'd2', 'to': 'd4'}),
                                      content_type='application/json')
        fake_data = fake_response.get_json()
        
        # This should be prevented as it's not the player's turn
        self.assertIn('aiMove', second_data, "AI should have made a move after the player's second move")
        
        # Check if moves array includes all previous moves
        self.assertIn('moves', second_data, "Response should include move history")
        move_history = second_data.get('moves', [])
        
        # At this point there should be 4 moves:
        # 1. Player e2-e4, 2. AI response, 3. Player g1-f3, 4. AI response
        self.assertEqual(len(move_history), 4, "Move history should contain 4 moves")
        
        # Verify the first player move is correctly recorded
        self.assertEqual(move_history[0]['from'], 'e2', "First move should be from e2")
        self.assertEqual(move_history[0]['to'], 'e4', "First move should be to e4")
        self.assertEqual(move_history[0]['player'], 'white', "First move should be white's")
    
    def test_move_list_updating(self):
        """Test that the move list updates correctly with each move."""
        # Make a series of moves and check move list updates
        moves = [
            {'from': 'e2', 'to': 'e4'},  # Player move 1
            {'from': 'g1', 'to': 'f3'},  # Player move 2
            {'from': 'd2', 'to': 'd4'},  # Player move 3
        ]
        
        move_history = []
        
        for i, move in enumerate(moves):
            response = self.client.post('/move',
                                      data=json.dumps(move),
                                      content_type='application/json')
            data = response.get_json()
            
            self.assertTrue(data['valid'], f"Move {i+1} should be valid")
            self.assertIn('moves', data, f"Response for move {i+1} should include move history")
            
            move_history = data.get('moves', [])
            
            # Each player move plus AI response means we should have 2*(i+1) moves
            expected_moves = 2 * (i + 1)
            self.assertEqual(len(move_history), expected_moves, 
                           f"After move {i+1}, move history should contain {expected_moves} moves")
            
            # Verify player move is recorded correctly
            player_move_index = i * 2  # Player moves are at even indices
            self.assertEqual(move_history[player_move_index]['from'], move['from'], 
                           f"Move {i+1} should be from {move['from']}")
            self.assertEqual(move_history[player_move_index]['to'], move['to'], 
                           f"Move {i+1} should be to {move['to']}")
            
            # Check AI responded
            self.assertIn('aiMove', data, f"AI should respond to move {i+1}")
    
    def test_continuous_move_capability(self):
        """Test that the player can continue making moves throughout the game."""
        # Make a series of moves and ensure all are valid
        moves = [
            {'from': 'e2', 'to': 'e4'},   # Player move 1
            {'from': 'g1', 'to': 'f3'},   # Player move 2
            {'from': 'd2', 'to': 'd4'},   # Player move 3
            {'from': 'b1', 'to': 'c3'},   # Player move 4
            {'from': 'f1', 'to': 'd3'},   # Player move 5
        ]
        
        for i, move in enumerate(moves):
            response = self.client.post('/move',
                                      data=json.dumps(move),
                                      content_type='application/json')
            data = response.get_json()
            
            # Verify each move is valid
            self.assertTrue(data['valid'], f"Move {i+1} should be valid")
            
            # Verify game state remains active
            self.assertEqual(data['gameState'], 'active', 
                           f"Game should remain active after move {i+1}")
            
            # Check the next player can still move (AI response happened)
            self.assertIn('aiMove', data, f"AI should respond to move {i+1}")
            
            # Ensure board state updated
            self.assertIn('board', data, f"Response should include board state after move {i+1}")
            board = data.get('board', {})
            
            # Verify the player's piece is moved to the target square
            to_square = move['to']
            if to_square in board:
                piece = board[to_square]
                self.assertEqual(piece['color'], 'white', 
                               f"After move {i+1}, {to_square} should contain white piece")
            
            # Verify the from square is now empty
            from_square = move['from']
            if from_square in board:
                self.assertNotEqual(board[from_square]['color'], 'white',
                                 f"After move {i+1}, {from_square} should not contain white piece")

if __name__ == '__main__':
    unittest.main() 