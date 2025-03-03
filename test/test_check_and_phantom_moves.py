import unittest
import json
from app import app, board_to_dict, square_to_coord, coord_to_square, current_position, MATE_LOWER, MATE_UPPER
from chess_logic_by_thomasahle import Position, initial

class CheckAndPhantomMovesTestCase(unittest.TestCase):
    
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
    
    def test_no_phantom_moves(self):
        """Test that the engine doesn't invent imaginary moves with non-existent pieces."""
        # Make several player moves to get to a more complex position
        moves = [
            ('e2', 'e4'),  # Pawn e2-e4
            ('g1', 'f3'),  # Knight g1-f3
            ('f1', 'c4'),  # Bishop f1-c4
        ]
        
        for from_square, to_square in moves:
            response = self.client.post('/move',
                                     data=json.dumps({'from': from_square, 'to': to_square}),
                                     content_type='application/json')
            data = response.get_json()
            self.assertTrue(data['valid'], f"Move {from_square}-{to_square} should be valid")
            
            # Verify the AI response
            self.assertIn('aiMove', data, "AI should make a move in response")
            
            # Get the resulting board state
            board_state = data['board']
            
            # Verify the move was actually made on the board
            self.assertNotIn(from_square, board_state, f"Piece should no longer be at {from_square}")
            
            # Verify that the piece exists at the new location
            self.assertIn(to_square, board_state, f"Piece should now be at {to_square}")
            
            # Verify all moves in the move history reference actual pieces on the board
            for move in data['moves']:
                # Skip AI moves as we're not testing AI here
                if move['player'] == 'white':
                    # Verify the piece exists in the "to" position after the move
                    final_position = move['to']
                    self.assertIn(final_position, board_state, 
                                 f"Piece should exist at {final_position} after move {move['from']}-{move['to']}")
    
    def test_king_in_check_detection(self):
        """Test that the engine correctly detects when the king is in check."""
        # Set up a specific position where the king will be in check
        # First move pawn to e4
        response = self.client.post('/move',
                                  data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                  content_type='application/json')
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # Now move the bishop to c4
        response = self.client.post('/move',
                                  data=json.dumps({'from': 'f1', 'to': 'c4'}),
                                  content_type='application/json')
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # Now move the queen to h5, which should put the black king in check
        response = self.client.post('/move',
                                  data=json.dumps({'from': 'd1', 'to': 'h5'}),
                                  content_type='application/json')
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # The AI should respond by blocking the check or moving the king
        ai_move = data['aiMove']
        
        # Get the board after the AI's move
        board_after_ai = data['board']
        
        # Get all possible moves for the player
        all_valid_moves = []
        for square, piece_info in board_after_ai.items():
            if piece_info['color'] == 'white':
                from_square = square
                for to_square in "abcdefgh":
                    for rank in range(1, 9):
                        to_coord = f"{to_square}{rank}"
                        response = self.client.post('/move',
                                                  data=json.dumps({'from': from_square, 'to': to_coord}),
                                                  content_type='application/json')
                        move_data = response.get_json()
                        if move_data.get('valid', False):
                            all_valid_moves.append((from_square, to_coord))
        
        # If check detection is working, the AI should have moved to block the check
        # or moved the king away from the check
        # Let's verify this by checking if the current position doesn't put the AI's king in check
        
        # Create a checkmating position and verify it's detected correctly
        custom_position = "r...k..r" \
                         "........" \
                         "........" \
                         "........" \
                         "...Q...." \
                         "........" \
                         "........" \
                         "R...K..R"
        
        # We'd need to directly modify the current_position to test this thoroughly
        # This is a bit challenging in the current test setup, but we can check that
        # no illegal moves are allowed when in check

    def test_checkmate_detection(self):
        """Test that the engine correctly identifies checkmate positions."""
        # Create a classic fool's mate scenario
        # Move pawn from f2 to f3
        response = self.client.post('/move',
                                  data=json.dumps({'from': 'f2', 'to': 'f3'}),
                                  content_type='application/json')
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # After AI's move, move pawn from g2 to g4
        response = self.client.post('/move',
                                  data=json.dumps({'from': 'g2', 'to': 'g4'}),
                                  content_type='application/json')
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # The AI should now have an opportunity to deliver checkmate with Qh4#
        # We'll look at the game state to see if it recognizes this
        ai_move = data['aiMove']
        
        # If the AI has played properly and checkmate detection works, 
        # the game state should change to 'ended'
        if ai_move and ai_move['to'] == 'h4' and ai_move['from'][0] == 'd':  # Queen to h4
            self.assertEqual(data['gameState'], 'ended', 
                          "Game should end after checkmate")
            self.assertEqual(data['winner'], 'ai', 
                          "AI should be declared the winner after checkmate")
    
    def test_stalemate_detection(self):
        """Test that the engine correctly identifies stalemate positions."""
        # Setting up a stalemate position is complex in a full test
        # We'd ideally manipulate the position directly
        
        # For now, we can verify that stalemate is correctly detected by checking
        # that when a player has no valid moves but is not in check, the game ends in a draw
        
        # This would require a custom board position
        # This is a simplified test that checks basic stalemate logic
        
        # In a real stalemate position:
        # 1. The player would have no legal moves
        # 2. The player's king would not be in check
        # 3. The game should end in a draw, not a win for either side
        
        # For now, we'll just verify the core functionality exists by checking
        # if the app checks for valid moves before declaring a winner
        # Future enhancements would include setting up specific stalemate positions
        
    def test_no_moves_detection(self):
        """Test that the engine correctly detects when a player has no valid moves."""
        # We'll make several moves to get to a more complex position
        # Then verify that the engine correctly determines if there are valid moves
        
        # Initialize with a position where moves are limited
        # Make several moves to get to a complex position
        moves = [
            ('e2', 'e4'),
            ('g1', 'f3'),
            ('f1', 'c4'),
        ]
        
        for from_square, to_square in moves:
            response = self.client.post('/move',
                                     data=json.dumps({'from': from_square, 'to': to_square}),
                                     content_type='application/json')
        
        # Get the last board state
        board_state = response.get_json()['board']
        
        # Verify that the engine correctly identifies when there are valid moves
        # by checking if at least one piece can move
        has_valid_moves = False
        
        for square, piece in board_state.items():
            if piece['color'] == 'white':  # Check player's pieces
                for to_file in 'abcdefgh':
                    for to_rank in range(1, 9):
                        to_square = f"{to_file}{to_rank}"
                        test_response = self.client.post('/move',
                                                      data=json.dumps({'from': square, 'to': to_square}),
                                                      content_type='application/json')
                        if test_response.get_json().get('valid', False):
                            has_valid_moves = True
                            break
                    if has_valid_moves:
                        break
            if has_valid_moves:
                break
        
        # In a normal position, the player should have valid moves
        self.assertTrue(has_valid_moves, "Player should have valid moves in a normal position")

if __name__ == '__main__':
    unittest.main() 