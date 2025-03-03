import unittest
import sys
import os
import json

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestFrontendFormats(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize a new game - specify difficulty to match what frontend would send
        response = self.client.post('/initialize', 
                                   json={'difficulty': 'easy'},
                                   content_type='application/json')
        self.initialize_data = json.loads(response.data.decode('utf-8'))
        
    def test_legal_moves_format(self):
        """Test the format of legal moves returned by the /move endpoint"""
        # Make a move
        response = self.client.post('/move', 
                                   json={'from': 'e2', 'to': 'e4'},
                                   content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        
        # Check that the response is valid
        self.assertTrue(data['valid'])
        
        # Verify that legalMoves contains the expected format
        self.assertIn('legalMoves', data)
        self.assertIsInstance(data['legalMoves'], list)
        
        # Check that each legal move has the correct structure
        for move in data['legalMoves']:
            with self.subTest(move=move):
                self.assertIn('from', move)
                self.assertIn('to', move)
                self.assertIsInstance(move['from'], str)
                self.assertIsInstance(move['to'], str)
                # Check that the square notations are valid
                self.assertRegex(move['from'], r'^[a-h][1-8]$')
                self.assertRegex(move['to'], r'^[a-h][1-8]$')
        
        # Print the legalMoves for debugging
        print("\nLegal moves returned by /move endpoint:")
        for move in data['legalMoves']:
            print(f"From {move['from']} to {move['to']}")
        
        # Check that the AI move format is correct
        if 'aiMove' in data and data['aiMove']:
            self.assertIn('from', data['aiMove'])
            self.assertIn('to', data['aiMove'])
            self.assertIsInstance(data['aiMove']['from'], str)
            self.assertIsInstance(data['aiMove']['to'], str)
            self.assertRegex(data['aiMove']['from'], r'^[a-h][1-8]$')
            self.assertRegex(data['aiMove']['to'], r'^[a-h][1-8]$')
            print(f"\nAI Move: From {data['aiMove']['from']} to {data['aiMove']['to']}")
    
    def test_board_format(self):
        """Test the format of the board state returned by the /move endpoint"""
        # Make a move
        response = self.client.post('/move', 
                                   json={'from': 'e2', 'to': 'e4'},
                                   content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        
        # Check that the board state is correctly formatted
        self.assertIn('board', data)
        self.assertIsInstance(data['board'], dict)
        
        # Check the format of each piece on the board
        for square, piece in data['board'].items():
            with self.subTest(square=square, piece=piece):
                self.assertRegex(square, r'^[a-h][1-8]$')
                self.assertIn('code', piece)
                self.assertIn('color', piece)
                self.assertIn('type', piece)
                self.assertIn(piece['color'], ['white', 'black'])

if __name__ == '__main__':
    unittest.main() 