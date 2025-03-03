import unittest
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestBackendMoveProcessing(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Initialize a new game before each test
        response = self.client.post('/initialize', 
                                   data=json.dumps({"difficulty": "easy"}), 
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify the game initialized correctly
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn('board', data)
        self.assertIn('e2', data['board'])  # Check for white pawn
        self.assertIn('e7', data['board'])  # Check for black pawn
    
    def tearDown(self):
        pass
    
    def test_move_white_pawn_updates_board(self):
        """Test that moving a white pawn from e2 to e4 correctly updates the board."""
        # Get initial board state
        response = self.client.post('/initialize', 
                                   data=json.dumps({"difficulty": "easy"}), 
                                   content_type='application/json')
        initial_board = response.get_json()['board']
        
        # Make sure e2 has a white pawn and e4 is empty
        self.assertIn('e2', initial_board)
        self.assertEqual(initial_board['e2']['type'], 'pawn')
        self.assertEqual(initial_board['e2']['color'], 'white')
        self.assertNotIn('e4', initial_board)
        
        # Make the move
        response = self.client.post('/move', 
                                   data=json.dumps({"from": "e2", "to": "e4"}), 
                                   content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # Verify board state updated correctly
        updated_board = data['board']
        
        # e2 should now be empty
        self.assertNotIn('e2', updated_board)
        
        # e4 should now have the white pawn
        self.assertIn('e4', updated_board)
        self.assertEqual(updated_board['e4']['type'], 'pawn')
        self.assertEqual(updated_board['e4']['color'], 'white')
        
        # Verify AI's move also updated the board
        self.assertIn('aiMove', data)
        ai_from = data['aiMove']['from']
        ai_to = data['aiMove']['to']
        
        # AI source square should be empty now
        self.assertNotIn(ai_from, updated_board)
        
        # AI destination square should have the moved piece
        self.assertIn(ai_to, updated_board)
        self.assertEqual(updated_board[ai_to]['color'], 'black')

    def test_move_knight_updates_board(self):
        """Test that moving a knight correctly updates the board."""
        # Get initial board state
        response = self.client.post('/initialize', 
                                   data=json.dumps({"difficulty": "easy"}), 
                                   content_type='application/json')
        initial_board = response.get_json()['board']
        
        # Make sure g1 has a white knight and f3 is empty
        self.assertIn('g1', initial_board)
        self.assertEqual(initial_board['g1']['type'], 'knight')
        self.assertEqual(initial_board['g1']['color'], 'white')
        self.assertNotIn('f3', initial_board)
        
        # Make the move
        response = self.client.post('/move', 
                                   data=json.dumps({"from": "g1", "to": "f3"}), 
                                   content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # Verify board state updated correctly
        updated_board = data['board']
        
        # g1 should now be empty
        self.assertNotIn('g1', updated_board)
        
        # f3 should now have the white knight
        self.assertIn('f3', updated_board)
        self.assertEqual(updated_board['f3']['type'], 'knight')
        self.assertEqual(updated_board['f3']['color'], 'white')

    def test_move_bishop_updates_board(self):
        """Test that moving a bishop correctly updates the board."""
        # First move a pawn to open a path for the bishop
        response = self.client.post('/move', 
                                   data=json.dumps({"from": "e2", "to": "e4"}), 
                                   content_type='application/json')
        
        # Now check initial state before bishop move
        response = self.client.post('/move', 
                                   data=json.dumps({"from": "f1", "to": "c4"}), 
                                   content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['valid'])
        
        # Verify board state updated correctly
        updated_board = data['board']
        
        # f1 should now be empty
        self.assertNotIn('f1', updated_board)
        
        # c4 should now have the white bishop
        self.assertIn('c4', updated_board)
        self.assertEqual(updated_board['c4']['type'], 'bishop')
        self.assertEqual(updated_board['c4']['color'], 'white')

    def test_capture_piece_updates_board(self):
        """Test that capturing a piece correctly updates the board."""
        # First move pieces to set up a capture
        
        # Move white pawn e2-e4
        self.client.post('/move', 
                        data=json.dumps({"from": "e2", "to": "e4"}), 
                        content_type='application/json')
        
        # Move white pawn d2-d4
        self.client.post('/move', 
                        data=json.dumps({"from": "d2", "to": "d4"}), 
                        content_type='application/json')
        
        # Move white pawn c2-c4
        self.client.post('/move', 
                        data=json.dumps({"from": "c2", "to": "c4"}), 
                        content_type='application/json')
        
        # Move white queen d1-a4 to set up for capture
        response = self.client.post('/move', 
                                   data=json.dumps({"from": "d1", "to": "a4"}), 
                                   content_type='application/json')
        
        data = response.get_json()
        updated_board = data['board']
        
        # Find a black piece that the queen can capture
        capture_target = None
        for square, piece in updated_board.items():
            if piece['color'] == 'black' and square[0] == 'a':  # Look for a piece on the a-file
                capture_target = square
                break
        
        if capture_target:
            # Attempt to capture the piece
            response = self.client.post('/move', 
                                       data=json.dumps({"from": "a4", "to": capture_target}), 
                                       content_type='application/json')
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            if data['valid']:
                # Verify board state updated correctly
                updated_board = data['board']
                
                # a4 should now be empty
                self.assertNotIn('a4', updated_board)
                
                # Target square should now have the white queen
                self.assertIn(capture_target, updated_board)
                self.assertEqual(updated_board[capture_target]['type'], 'queen')
                self.assertEqual(updated_board[capture_target]['color'], 'white')
            
    def test_sequence_of_moves(self):
        """Test a sequence of moves to ensure board state is consistently updated."""
        # Initialize a new game
        response = self.client.post('/initialize', 
                                   data=json.dumps({"difficulty": "easy"}), 
                                   content_type='application/json')
        initial_board = response.get_json()['board']
        
        # Define a sequence of moves
        moves = [
            ("e2", "e4"),  # White pawn
            ("g1", "f3"),  # White knight
            ("f1", "c4"),  # White bishop
        ]
        
        for from_square, to_square in moves:
            # Make the move
            response = self.client.post('/move', 
                                       data=json.dumps({"from": from_square, "to": to_square}), 
                                       content_type='application/json')
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['valid'])
            
            # Verify board state updated correctly
            updated_board = data['board']
            
            # From square should now be empty
            self.assertNotIn(from_square, updated_board)
            
            # To square should now have the piece
            self.assertIn(to_square, updated_board)
            
            # Print debug info about the AI's move
            if 'aiMove' in data:
                ai_from = data['aiMove']['from']
                ai_to = data['aiMove']['to']
                print(f"AI moved from {ai_from} to {ai_to}")
                
                # AI source square should be empty
                self.assertNotIn(ai_from, updated_board)
                
                # AI destination square should have the moved piece
                self.assertIn(ai_to, updated_board)
                self.assertEqual(updated_board[ai_to]['color'], 'black')

if __name__ == '__main__':
    unittest.main() 