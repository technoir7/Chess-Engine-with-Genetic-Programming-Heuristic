import unittest
import json
from app import app

class DoubleMoveIssueTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_no_double_moves_after_first_move(self):
        """Test that after player makes first move, program doesn't make player's second move automatically."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        init_data = init_response.get_json()
        
        # Verify that the current player is properly set to 'white' initially
        self.assertEqual(init_data.get('currentPlayer'), 'white', "Game should start with player's turn (white)")
        
        # Make first move (e2-e4)
        first_move_response = self.client.post('/move',
                                  data=json.dumps({"from": "e2", "to": "e4"}),
                                  content_type='application/json')
        first_move_data = first_move_response.get_json()
        
        # Verify move was accepted
        self.assertTrue(first_move_data.get('valid'), "First move should be valid")
        
        # Verify AI made a move in response
        self.assertIn('aiMove', first_move_data, "AI should make a move in response")
        
        # Check that the current player is properly set to 'white' after AI's move
        self.assertEqual(first_move_data.get('currentPlayer'), 'white', 
                        "After AI's move, it should be player's turn again (white)")
        
        # Now make a second move (g1-f3)
        second_move_response = self.client.post('/move',
                                   data=json.dumps({"from": "g1", "to": "f3"}),
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        
        # Verify second move was accepted
        self.assertTrue(second_move_data.get('valid'), "Second move should be valid")
        
        # Verify AI made a move in response
        self.assertIn('aiMove', second_move_data, "AI should make a move in response to second move")
        
        # Check that the current player is properly set to 'white' after AI's second move
        self.assertEqual(second_move_data.get('currentPlayer'), 'white', 
                        "After AI's second move, it should be player's turn again (white)")
        
        # Now try to make a third move (f1-c4)
        third_move_response = self.client.post('/move',
                                  data=json.dumps({"from": "f1", "to": "c4"}),
                                  content_type='application/json')
        third_move_data = third_move_response.get_json()
        
        # Verify third move was accepted
        self.assertTrue(third_move_data.get('valid'), "Third move should be valid")
    
    def test_player_can_make_moves_after_second_turn(self):
        """Test that player can still make moves after the first round of moves."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        
        # Make first player move
        first_move_response = self.client.post('/move',
                                  data=json.dumps({"from": "e2", "to": "e4"}),
                                  content_type='application/json')
        
        # Verify AI response contains current player information
        first_move_data = first_move_response.get_json()
        self.assertIn('currentPlayer', first_move_data, "Response should include currentPlayer")
        
        # Verify it's the player's turn again
        self.assertEqual(first_move_data.get('currentPlayer'), 'white', 
                        "After AI's move, it should be player's turn again")
        
        # Now try to make a second move as the player
        second_move_response = self.client.post('/move',
                                   data=json.dumps({"from": "d2", "to": "d4"}),
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        
        # Verify the move was valid
        self.assertTrue(second_move_data.get('valid'), "Player should be able to make a second move")
        
        # Make sure move was actually registered by checking board state
        board_after_second_move = second_move_data.get('board', {})
        self.assertIn('d4', board_after_second_move, "Pawn should be at d4 after player's second move")
        self.assertEqual(board_after_second_move['d4']['type'], 'p', "Piece at d4 should be a pawn")
        self.assertEqual(board_after_second_move['d4']['color'], 'white', "Piece at d4 should be white")
    
    def test_move_tracking_consistency(self):
        """Test that moves are properly tracked and turns alternate correctly."""
        # Initialize a game
        init_response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        
        # Make a series of moves and track them
        move_sequence = [
            {"from": "e2", "to": "e4"},  # Player 1st move
            {"from": "g1", "to": "f3"},  # Player 2nd move
            {"from": "f1", "to": "c4"},  # Player 3rd move
        ]
        
        all_moves = []
        current_player = 'white'
        
        for move_num, move in enumerate(move_sequence, 1):
            # Assert it's player's turn before making move
            self.assertEqual(current_player, 'white', f"Before move {move_num}, it should be player's turn")
            
            # Make the move
            response = self.client.post('/move',
                                     data=json.dumps(move),
                                     content_type='application/json')
            data = response.get_json()
            
            # Verify move was accepted
            self.assertTrue(data.get('valid'), f"Move {move_num} should be valid")
            
            # Add player move to our tracking
            all_moves.append({
                'from': move['from'],
                'to': move['to'],
                'player': 'white'
            })
            
            # Add AI move to our tracking
            if 'aiMove' in data:
                all_moves.append({
                    'from': data['aiMove']['from'],
                    'to': data['aiMove']['to'],
                    'player': 'black'
                })
            
            # Verify the server's move history matches our tracking
            server_moves = data.get('moves', [])
            self.assertEqual(len(server_moves), len(all_moves), 
                            f"After move {move_num}, move history length should match")
            
            # Verify it's player's turn again
            current_player = data.get('currentPlayer')
            self.assertEqual(current_player, 'white', 
                            f"After move {move_num} and AI response, it should be player's turn again")
    
    def test_complete_game_flow_sequence(self):
        """Test a complete sequence that tries to replicate the issue where player can't make moves."""
        # Initialize a game
        init_response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        init_data = init_response.get_json()
        
        # Print detailed debug information
        print("\n=== DETAILED DEBUG INFO FOR COMPLETE GAME FLOW TEST ===")
        print(f"Initial state - current player: {init_data.get('currentPlayer')}")
        
        # Make player's first move
        first_move_response = self.client.post('/move',
                                   data=json.dumps({"from": "e2", "to": "e4"}),
                                   content_type='application/json')
        first_move_data = first_move_response.get_json()
        
        # Print detailed info about the response
        print("\nAfter player's first move:")
        print(f"  Valid move: {first_move_data.get('valid')}")
        print(f"  Current player: {first_move_data.get('currentPlayer')}")
        print(f"  AI move: {first_move_data.get('aiMove')}")
        print(f"  Move history: {first_move_data.get('moves')}")
        
        # Get board state
        first_board = first_move_data.get('board', {})
        
        # Verify it's now player's turn again
        self.assertEqual(first_move_data.get('currentPlayer'), 'white', 
                        "After AI's move, it should be player's turn again")
        
        # Test immediately making a second player move
        second_move_response = self.client.post('/move',
                                   data=json.dumps({"from": "d2", "to": "d4"}),
                                   content_type='application/json')
        second_move_data = second_move_response.get_json()
        
        # Print detailed info about the second move response
        print("\nAfter player's second move:")
        print(f"  Valid move: {second_move_data.get('valid')}")
        print(f"  Current player: {second_move_data.get('currentPlayer')}")
        print(f"  AI move: {second_move_data.get('aiMove')}")
        print(f"  Move history: {second_move_data.get('moves')}")
        
        # Get updated board state
        second_board = second_move_data.get('board', {})
        
        # Verify player's second move was successfully made
        self.assertIn('d4', second_board, "Player's second move (d2-d4) should be reflected in board state")
        self.assertEqual(second_board.get('d4', {}).get('type'), 'p', "Piece at d4 should be a pawn")
        self.assertEqual(second_board.get('d4', {}).get('color'), 'white', "Piece at d4 should be white")
        
        # Now try making a third move
        third_move_response = self.client.post('/move',
                                  data=json.dumps({"from": "b1", "to": "c3"}),
                                  content_type='application/json')
        third_move_data = third_move_response.get_json()
        
        # Print detailed info about the third move response
        print("\nAfter player's third move:")
        print(f"  Valid move: {third_move_data.get('valid')}")
        print(f"  Current player: {third_move_data.get('currentPlayer')}")
        print(f"  AI move: {third_move_data.get('aiMove')}")
        print(f"  Move history: {third_move_data.get('moves')}")
        
        # Verify third move was valid
        self.assertTrue(third_move_data.get('valid'), "Player should be able to make a third move")
        
        # Get updated board state
        third_board = third_move_data.get('board', {})
        
        # Verify player's third move was successfully made
        self.assertIn('c3', third_board, "Player's third move (b1-c3) should be reflected in board state")
        self.assertEqual(third_board.get('c3', {}).get('type'), 'n', "Piece at c3 should be a knight")
        self.assertEqual(third_board.get('c3', {}).get('color'), 'white', "Piece at c3 should be white")
        
        # Check that move history is consistent
        move_history = third_move_data.get('moves', [])
        
        # Expected moves: player e2-e4, AI move, player d2-d4, AI move, player b1-c3, AI move
        self.assertEqual(len(move_history), 6, "Should have recorded 6 moves (3 player, 3 AI)")
        
        # Categorize moves by player
        player_moves = [move for move in move_history if move.get('player') == 'white']
        ai_moves = [move for move in move_history if move.get('player') == 'black']
        
        # Verify correct number of moves by each player
        self.assertEqual(len(player_moves), 3, "Should have 3 player moves")
        self.assertEqual(len(ai_moves), 3, "Should have 3 AI moves")
        
        # Print summary
        print("\nMove history summary:")
        for i, move in enumerate(move_history):
            print(f"  Move {i+1}: {move.get('player')} moved from {move.get('from')} to {move.get('to')}")
        
        print("=== TEST COMPLETE ===\n")

if __name__ == '__main__':
    unittest.main() 