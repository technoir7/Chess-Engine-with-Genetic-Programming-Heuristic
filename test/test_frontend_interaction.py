import unittest
import sys
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import threading
import socket
import subprocess

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class MockBrowser:
    """A mock for simulating browser interactions without using Selenium"""
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def initialize_game(self, difficulty='easy'):
        """Initialize a new game"""
        response = self.session.post(
            f"{self.base_url}/initialize",
            json={"difficulty": difficulty},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    
    def make_move(self, from_square, to_square):
        """Make a move using the /move endpoint"""
        response = self.session.post(
            f"{self.base_url}/move",
            json={"from": from_square, "to": to_square},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    
    def simulate_frontend_sequence(self):
        """Simulate a sequence of interactions like a frontend would make"""
        # Initialize the game
        init_data = self.initialize_game()
        print("Game initialized with response:", json.dumps(init_data, indent=2)[:200] + "...")
        
        # Make a series of moves
        moves = [
            ("e2", "e4"),  # First move: e2 to e4
            # The AI will respond automatically
            ("d2", "d4"),  # Second move: d2 to d4
            # The AI will respond automatically
        ]
        
        results = []
        for from_square, to_square in moves:
            print(f"\nMaking move from {from_square} to {to_square}...")
            move_data = self.make_move(from_square, to_square)
            print(f"Move response received - valid: {move_data.get('valid', False)}")
            
            if move_data.get('aiMove'):
                print(f"AI responded with: {move_data['aiMove']['from']} to {move_data['aiMove']['to']}")
            
            # Check legal moves format
            legal_moves = move_data.get('legalMoves', [])
            print(f"Received {len(legal_moves)} legal moves")
            for move in legal_moves[:3]:  # Print first 3 for brevity
                print(f"  {move['from']} -> {move['to']}")
            
            results.append(move_data)
            time.sleep(0.5)  # Brief pause between moves
        
        return results

class TestFrontendInteraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test class - start a Flask server in a separate thread"""
        # Start Flask in a thread
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        # Skip starting the Flask server in a thread since we're using the test client
        cls.mock_browser = MockBrowser()
        
    def test_simulate_frontend_moves(self):
        """Test simulating frontend move interactions"""
        # Initialize the game
        response = self.client.post('/initialize', 
                                  json={'difficulty': 'easy'},
                                  content_type='application/json')
        init_data = json.loads(response.data.decode('utf-8'))
        self.assertIn('board', init_data)
        
        # Make a move
        response = self.client.post('/move',
                                  json={'from': 'e2', 'to': 'e4'},
                                  content_type='application/json')
        move_data = json.loads(response.data.decode('utf-8'))
        
        # Verify the move was successful
        self.assertTrue(move_data.get('valid', False))
        self.assertIn('board', move_data)
        self.assertIn('aiMove', move_data)
        
        # Check that e2 is now empty and e4 has the pawn
        board = move_data['board']
        self.assertNotIn('e2', board)  # The piece has moved from e2
        self.assertIn('e4', board)     # The piece is now at e4
        
        # Check that e4 contains a white pawn
        e4_piece = board['e4']
        self.assertEqual(e4_piece['color'], 'white')
        self.assertEqual(e4_piece['type'], 'p')
        
        # Check legal moves format
        self.assertIn('legalMoves', move_data)
        self.assertIsInstance(move_data['legalMoves'], list)
        
        # Check AI move format
        ai_move = move_data.get('aiMove')
        self.assertIsNotNone(ai_move)
        self.assertIn('from', ai_move)
        self.assertIn('to', ai_move)
    
    def test_mock_browser_interaction(self):
        """Test simulating the browser interaction with the API"""
        # This test simulates how a real browser JavaScript would interact with the API
        moves_data = self.mock_browser.simulate_frontend_sequence()
        
        # Verify the sequence worked
        self.assertTrue(all(move.get('valid', False) for move in moves_data))
        
        # Check the final state
        final_state = moves_data[-1]
        self.assertIn('board', final_state)
        self.assertIn('legalMoves', final_state)

if __name__ == "__main__":
    unittest.main() 