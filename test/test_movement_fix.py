import unittest
import json
import sys
import os

# Add the parent directory to the path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, board_to_dict, square_to_coord, coord_to_square
from chess_logic_by_thomasahle import Position, initial

class TestMovementFix(unittest.TestCase):
    
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
    
    def test_coordinate_conversion(self):
        """Test the coordinate conversion functions."""
        # Test key coordinates
        test_cases = [
            ('a1', 91),
            ('h1', 98),
            ('a8', 21),
            ('h8', 28),
            ('e2', 85),
            ('e4', 65),
            ('d5', 54),
        ]
        
        for square, coord in test_cases:
            self.assertEqual(square_to_coord(square), coord, f"square_to_coord('{square}') should return {coord}")
            self.assertEqual(coord_to_square(coord), square, f"coord_to_square({coord}) should return '{square}'")
    
    def test_pawn_movement(self):
        """Test that pawns can move correctly."""
        # Test e2 to e4 (two-square move)
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e2", "to": "e4"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        self.assertTrue(move_data.get('valid', False), "Move e2-e4 should be valid")
        self.assertIn('e4', move_data.get('board', {}), "Board should have a piece at e4 after move")
        self.assertNotIn('e2', move_data.get('board', {}), "Board should not have a piece at e2 after move")
        
        # Reset game state
        self.setUp()
        
        # Test e2 to e3 (one-square move)
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e2", "to": "e3"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        self.assertTrue(move_data.get('valid', False), "Move e2-e3 should be valid")
        self.assertIn('e3', move_data.get('board', {}), "Board should have a piece at e3 after move")
        self.assertNotIn('e2', move_data.get('board', {}), "Board should not have a piece at e2 after move")
    
    def test_knight_movement(self):
        """Test that knights can move correctly."""
        # Test g1 to f3
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "g1", "to": "f3"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        self.assertTrue(move_data.get('valid', False), "Move g1-f3 should be valid")
        self.assertIn('f3', move_data.get('board', {}), "Board should have a piece at f3 after move")
        self.assertNotIn('g1', move_data.get('board', {}), "Board should not have a piece at g1 after move")
        
        # Knight piece should be preserved
        knight = move_data.get('board', {}).get('f3', {})
        # Accept either 'n' or 'knight' as valid type values
        self.assertIn(knight.get('type'), ['n', 'knight'], "Piece should be a knight")
        self.assertEqual(knight.get('color'), 'white', "Piece should still be white")
    
    def test_invalid_moves(self):
        """Test that invalid moves are rejected."""
        # Try moving a piece to an invalid square
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e2", "to": "e6"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        self.assertFalse(move_data.get('valid', True), "Move e2-e6 should be invalid")
        
        # Get fresh board state by reinitializing
        init_response = self.client.post('/initialize',
                                     data=json.dumps({"difficulty": "easy"}),
                                     content_type='application/json')
        init_data = init_response.get_json()
        self.assertIn('e2', init_data.get('board', {}), "Piece should still be at e2")
        self.assertNotIn('e6', init_data.get('board', {}), "No piece should be at e6")
        
        # Try moving a piece that's not there
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e4", "to": "e5"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        self.assertFalse(move_data.get('valid', True), "Move e4-e5 should be invalid")
        
        # Try moving an opponent's piece
        move_response = self.client.post('/move',
                                       data=json.dumps({"from": "e7", "to": "e5"}),
                                       content_type='application/json')
        move_data = move_response.get_json()
        
        self.assertFalse(move_data.get('valid', True), "Move e7-e5 should be invalid")
        
        # Check initial board again
        init_response = self.client.post('/initialize',
                                     data=json.dumps({"difficulty": "easy"}),
                                     content_type='application/json')
        init_data = init_response.get_json()
        self.assertIn('e7', init_data.get('board', {}), "Piece should still be at e7")
    
    def test_sequence_of_moves(self):
        """Test a sequence of valid moves."""
        # 1. e2 to e4
        move1 = self.client.post('/move',
                               data=json.dumps({"from": "e2", "to": "e4"}),
                               content_type='application/json')
        data1 = move1.get_json()
        self.assertTrue(data1.get('valid', False), "First move should be valid")
        
        # 2. g1 to f3
        move2 = self.client.post('/move',
                               data=json.dumps({"from": "g1", "to": "f3"}),
                               content_type='application/json')
        data2 = move2.get_json()
        self.assertTrue(data2.get('valid', False), "Second move should be valid")
        
        # 3. f1 to c4
        move3 = self.client.post('/move',
                               data=json.dumps({"from": "f1", "to": "c4"}),
                               content_type='application/json')
        data3 = move3.get_json()
        self.assertTrue(data3.get('valid', False), "Third move should be valid")
        
        # Check the final board state
        board = data3.get('board', {})
        self.assertIn('e4', board, "Pawn should be at e4")
        self.assertIn('f3', board, "Knight should be at f3")
        self.assertIn('c4', board, "Bishop should be at c4")
        
        # Check move history
        moves = data3.get('moves', [])
        move_list = [(m.get('from'), m.get('to')) for m in moves if m.get('player') == 'white']
        expected_moves = [('e2', 'e4'), ('g1', 'f3'), ('f1', 'c4')]
        
        for expected in expected_moves:
            self.assertIn(expected, move_list, f"Move history should include {expected}")

if __name__ == '__main__':
    unittest.main() 