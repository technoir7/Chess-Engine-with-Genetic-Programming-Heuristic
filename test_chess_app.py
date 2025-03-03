import unittest
import json
from app import app, board_to_dict, square_to_coord, coord_to_square
from chess_logic_by_thomasahle import Position, initial, MATE_LOWER, MATE_UPPER

class ChessAppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Clear any global state
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    def test_index_route(self):
        """Test that the index route returns the HTML page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Genetic Chess Engine', response.data)

    def test_initialize_game(self):
        """Test that we can initialize a new game."""
        response = self.client.post('/initialize',
                                   data=json.dumps({'difficulty': 'medium'}),
                                   content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('board', data)
        self.assertIn('gameState', data)
        self.assertEqual(data['gameState'], 'active')
        
        # Check that the initial board has all pieces in the right places
        board = data['board']
        # Check a few key positions (not exhaustive)
        self.assertIn('a1', board)  # White rook
        self.assertEqual(board['a1']['type'], 'r')
        self.assertEqual(board['a1']['color'], 'white')
        
        self.assertIn('e1', board)  # White king
        self.assertEqual(board['e1']['type'], 'k')
        self.assertEqual(board['e1']['color'], 'white')
        
        self.assertIn('a8', board)  # Black rook
        self.assertEqual(board['a8']['type'], 'r')
        self.assertEqual(board['a8']['color'], 'black')
        
        self.assertIn('e8', board)  # Black king
        self.assertEqual(board['e8']['type'], 'k')
        self.assertEqual(board['e8']['color'], 'black')

    def test_coord_conversion(self):
        """Test the coordinate conversion functions."""
        # Test square to coord
        self.assertEqual(square_to_coord('a1'), 112)  # Bottom left
        self.assertEqual(square_to_coord('h1'), 119)  # Bottom right
        self.assertEqual(square_to_coord('a8'), 0)    # Top left
        self.assertEqual(square_to_coord('h8'), 7)    # Top right
        self.assertEqual(square_to_coord('e4'), 68)   # Center
        
        # Test coord to square
        self.assertEqual(coord_to_square(112), 'a1')
        self.assertEqual(coord_to_square(119), 'h1')
        self.assertEqual(coord_to_square(0), 'a8')
        self.assertEqual(coord_to_square(7), 'h8')
        self.assertEqual(coord_to_square(68), 'e4')

    def test_board_to_dict(self):
        """Test the board_to_dict function."""
        position = Position(initial, 0, (True, True), (True, True), 0, 0)
        board_dict = board_to_dict(position)
        
        # Check a few key positions
        self.assertIn('a1', board_dict)
        self.assertEqual(board_dict['a1']['type'], 'r')
        self.assertEqual(board_dict['a1']['color'], 'white')
        
        self.assertIn('e1', board_dict)
        self.assertEqual(board_dict['e1']['type'], 'k')
        
        self.assertIn('a8', board_dict)
        self.assertEqual(board_dict['a8']['type'], 'r')
        self.assertEqual(board_dict['a8']['color'], 'black')

    def test_make_valid_move(self):
        """Test making a valid move."""
        # First initialize a game
        self.client.post('/initialize',
                        data=json.dumps({'difficulty': 'easy'}),
                        content_type='application/json')
        
        # Make a valid move (e2-e4 pawn move)
        response = self.client.post('/move',
                                   data=json.dumps({'from': 'e2', 'to': 'e4'}),
                                   content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['valid'])
        self.assertIn('aiMove', data)  # AI should respond with a move
        self.assertIn('board', data)   # Updated board should be returned

    def test_make_invalid_move(self):
        """Test making an invalid move."""
        # First initialize a game
        self.client.post('/initialize',
                        data=json.dumps({'difficulty': 'easy'}),
                        content_type='application/json')
        
        # Make an invalid move (a1-h8 rook can't move diagonally)
        response = self.client.post('/move',
                                   data=json.dumps({'from': 'a1', 'to': 'h8'}),
                                   content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['valid'])
        self.assertIn('message', data)  # Should have error message
        self.assertIn('board', data)    # Original board should be returned

if __name__ == '__main__':
    unittest.main() 