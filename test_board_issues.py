import unittest
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial
import json

class ChessBoardIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_initial_piece_positions(self):
        """Test that pieces start in the correct positions."""
        response = self.client.post('/initialize',
                                   data='{"difficulty": "medium"}',
                                   content_type='application/json')
        data = response.get_json()
        
        # Check that we have the board data
        self.assertIn('board', data)
        board = data['board']
        
        # Check white pieces (bottom row)
        self.assertEqual(board['a1']['type'], 'r', "White rook should be at a1")
        self.assertEqual(board['a1']['color'], 'white')
        self.assertEqual(board['b1']['type'], 'n', "White knight should be at b1")
        self.assertEqual(board['c1']['type'], 'b', "White bishop should be at c1") 
        self.assertEqual(board['d1']['type'], 'q', "White queen should be at d1")
        self.assertEqual(board['e1']['type'], 'k', "White king should be at e1")
        self.assertEqual(board['f1']['type'], 'b', "White bishop should be at f1")
        self.assertEqual(board['g1']['type'], 'n', "White knight should be at g1")
        self.assertEqual(board['h1']['type'], 'r', "White rook should be at h1")
        
        # Check white pawns (second row)
        for file in "abcdefgh":
            self.assertEqual(board[f'{file}2']['type'], 'p', f"White pawn should be at {file}2")
            self.assertEqual(board[f'{file}2']['color'], 'white')
        
        # Check black pieces (top row)
        self.assertEqual(board['a8']['type'], 'r', "Black rook should be at a8")
        self.assertEqual(board['a8']['color'], 'black')
        self.assertEqual(board['b8']['type'], 'n', "Black knight should be at b8")
        self.assertEqual(board['c8']['type'], 'b', "Black bishop should be at c8")
        self.assertEqual(board['d8']['type'], 'q', "Black queen should be at d8")
        self.assertEqual(board['e8']['type'], 'k', "Black king should be at e8")
        self.assertEqual(board['f8']['type'], 'b', "Black bishop should be at f8")
        self.assertEqual(board['g8']['type'], 'n', "Black knight should be at g8")
        self.assertEqual(board['h8']['type'], 'r', "Black rook should be at h8")
        
        # Check black pawns (seventh row)
        for file in "abcdefgh":
            self.assertEqual(board[f'{file}7']['type'], 'p', f"Black pawn should be at {file}7")
            self.assertEqual(board[f'{file}7']['color'], 'black')
    
    def test_no_black_text_on_board(self):
        """Test that there's no 'black' text appearing on the board."""
        response = self.client.post('/initialize',
                                   data='{"difficulty": "medium"}',
                                   content_type='application/json')
        data = response.get_json()
        
        # Count black pieces directly from the board dictionary
        board = data['board']
        black_pieces = [p for p in board.values() if p.get('color') == 'black']
        
        # There should be 16 black pieces total (8 pawns, 2 rooks, 2 knights, 2 bishops, 1 queen, 1 king)
        self.assertEqual(len(black_pieces), 16, "There should be exactly 16 black pieces")
        
        # Verify that the word 'black' only appears as the color property by checking each piece
        for square, piece in board.items():
            if 'black' in piece.get('color', ''):
                # This is fine - it's in the color property
                self.assertEqual(piece.get('color'), 'black', f"Square {square} has 'black' in an unexpected format")
            else:
                # If 'black' isn't in the color property, it shouldn't be in any property of this piece
                for prop_name, prop_value in piece.items():
                    self.assertNotIn('black', str(prop_value).lower(), 
                                    f"Square {square} contains 'black' in property {prop_name} with value {prop_value}")
    
    def test_piece_movement(self):
        """Test that pieces can move correctly."""
        # Initialize game
        self.client.post('/initialize',
                          data='{"difficulty": "easy"}',
                          content_type='application/json')
        
        # Make a valid pawn move (e2-e4)
        response = self.client.post('/move',
                                   data='{"from": "e2", "to": "e4"}',
                                   content_type='application/json')
        data = response.get_json()
        
        # Check that the move was accepted as valid
        self.assertTrue(data['valid'], "The pawn move e2-e4 should be valid")
        
        # Check that the pawn has actually moved to e4
        board = data['board']
        self.assertIn('e4', board, "Pawn should now be at e4")
        self.assertEqual(board['e4']['type'], 'p', "Piece at e4 should be a pawn")
        self.assertEqual(board['e4']['color'], 'white', "Pawn at e4 should be white")
        
        # Check that e2 is now empty (not in the board dictionary)
        self.assertNotIn('e2', board, "Square e2 should now be empty")
        
        # AI should have made a move in response
        self.assertIn('aiMove', data, "AI should have made a move")
        ai_move = data['aiMove']
        self.assertIn('from', ai_move)
        self.assertIn('to', ai_move)
        
        # Test another valid move - knight move
        response = self.client.post('/move',
                                   data='{"from": "g1", "to": "f3"}',
                                   content_type='application/json')
        data = response.get_json()
        
        # Check that the move was accepted as valid
        self.assertTrue(data['valid'], "The knight move g1-f3 should be valid")
        
        # Check that the knight has actually moved to f3
        board = data['board']
        self.assertIn('f3', board, "Knight should now be at f3")
        self.assertEqual(board['f3']['type'], 'n', "Piece at f3 should be a knight")
        self.assertEqual(board['f3']['color'], 'white', "Knight at f3 should be white")
        
        # Check that g1 is now empty
        self.assertNotIn('g1', board, "Square g1 should now be empty")

if __name__ == '__main__':
    unittest.main() 