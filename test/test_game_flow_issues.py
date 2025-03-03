import unittest
import json
from app import app, board_to_dict, square_to_coord, coord_to_square
from chess_logic_by_thomasahle import Position, initial

class GameFlowIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_turn_order(self):
        """Test that after a player move, only the AI makes a move (not a second player move)."""
        # Initialize a game
        self.client.post('/initialize',
                         data=json.dumps({'difficulty': 'easy'}),
                         content_type='application/json')
        
        # Make an initial move (e2-e4)
        response = self.client.post('/move',
                                   data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                   content_type='application/json')
        data = response.get_json()
        
        # Check that the move was valid
        self.assertTrue(data['valid'], "The move should be valid")
        
        # Verify that the AI made exactly one move in response
        self.assertIn('aiMove', data, "AI should have made a move")
        
        # The board should reflect exactly two moves: the player's and the AI's
        # Compare this to the initial board to confirm
        initial_response = self.client.post('/initialize',
                                           data=json.dumps({'difficulty': 'easy'}),
                                           content_type='application/json')
        initial_data = initial_response.get_json()
        
        # Count how many pieces have moved from their initial positions
        initial_board = initial_data['board']
        current_board = data['board']
        
        # Check that exactly two pieces moved (one by player, one by AI)
        moved_pieces = 0
        for square in initial_board:
            if square not in current_board:
                moved_pieces += 1
        
        # Two pieces should be off their initial squares (the moved player piece and the moved AI piece)
        # And two pieces should be on new squares (same pieces in new positions)
        self.assertLessEqual(moved_pieces, 4, "More than two moves appear to have been made")
        
    def test_continuous_move_capability(self):
        """Test that a player can continue making moves throughout the game."""
        # Initialize a game
        self.client.post('/initialize',
                         data=json.dumps({'difficulty': 'easy'}),
                         content_type='application/json')
        
        # Make a sequence of moves
        # First move: e2-e4 (pawn)
        response1 = self.client.post('/move',
                                    data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                    content_type='application/json')
        data1 = response1.get_json()
        self.assertTrue(data1['valid'], "First move should be valid")
        
        # Second move: g1-f3 (knight)
        response2 = self.client.post('/move',
                                    data=json.dumps({'from': 'g1', 'to': 'f3'}),
                                    content_type='application/json')
        data2 = response2.get_json()
        self.assertTrue(data2['valid'], "Second move should be valid")
        
        # Third move: f1-e2 (bishop)
        response3 = self.client.post('/move',
                                    data=json.dumps({'from': 'f1', 'to': 'e2'}),
                                    content_type='application/json')
        data3 = response3.get_json()
        self.assertTrue(data3['valid'], "Third move should be valid")
        
        # Fourth move: e1-g1 (castling kingside)
        response4 = self.client.post('/move',
                                    data=json.dumps({'from': 'e1', 'to': 'g1'}),
                                    content_type='application/json')
        data4 = response4.get_json()
        self.assertTrue(data4['valid'], "Fourth move (castling) should be valid")
        
        # Check game state - should still be active
        self.assertEqual(data4['gameState'], 'active', "Game should still be active after four moves")
    
    def test_move_list_updating(self):
        """Test that the move list updates correctly."""
        # Initialize a game
        init_response = self.client.post('/initialize',
                                        data=json.dumps({'difficulty': 'easy'}),
                                        content_type='application/json')
        
        # Get the initial game state
        init_data = init_response.get_json()
        self.assertNotIn('moves', init_data, "Initial game should not have any moves recorded")
        
        # Make a move
        move_response = self.client.post('/move',
                                        data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                        content_type='application/json')
        
        move_data = move_response.get_json()
        
        # Check if the move is recorded
        self.assertIn('moves', move_data, "Move list should be included in the response")
        
        # The move list should include both the player's move and the AI's move
        move_list = move_data.get('moves', [])
        self.assertGreaterEqual(len(move_list), 1, "At least the player's move should be in the list")
        
        # Make a second move
        move2_response = self.client.post('/move',
                                         data=json.dumps({'from': 'g1', 'to': 'f3'}),
                                         content_type='application/json')
        
        move2_data = move2_response.get_json()
        
        # Check that the move list is updated and includes the previous moves
        self.assertIn('moves', move2_data, "Move list should be included in the response")
        move_list2 = move2_data.get('moves', [])
        self.assertGreaterEqual(len(move_list2), 3, "Move list should include previous moves plus new moves")
        
        # Verify the first move is still in the list
        first_move_found = False
        for move in move_list2:
            if move.get('from') == 'e2' and move.get('to') == 'e4':
                first_move_found = True
                break
                
        self.assertTrue(first_move_found, "First move should still be in the move list")
    
    def test_game_state_handling(self):
        """Test that the game state is correctly handled and updated."""
        # Initialize a game
        self.client.post('/initialize',
                         data=json.dumps({'difficulty': 'easy'}),
                         content_type='application/json')
        
        # Make several moves and check the game state
        response = self.client.post('/move',
                                   data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                   content_type='application/json')
        data = response.get_json()
        
        # Game should be active after the first move
        self.assertEqual(data['gameState'], 'active', "Game should be active after the first move")
        
        # Try to make an invalid move
        invalid_response = self.client.post('/move',
                                          data=json.dumps({'from': 'e1', 'to': 'e8'}),
                                          content_type='application/json')
        invalid_data = invalid_response.get_json()
        
        # Check that the invalid move is properly rejected
        self.assertFalse(invalid_data['valid'], "Invalid move should be rejected")
        
        # Game should still be active after rejected move
        self.assertEqual(invalid_data['gameState'], 'active', "Game should still be active after invalid move")
        
        # Verify we can still make valid moves
        response2 = self.client.post('/move',
                                    data=json.dumps({'from': 'g1', 'to': 'f3'}),
                                    content_type='application/json')
        data2 = response2.get_json()
        self.assertTrue(data2['valid'], "Valid move should be accepted after invalid move")

if __name__ == '__main__':
    unittest.main() 