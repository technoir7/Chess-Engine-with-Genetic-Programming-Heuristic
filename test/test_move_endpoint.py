import unittest
import json
import sys
import os
import requests

# Add the parent directory to the path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestMoveEndpoint(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize a new game 
        init_response = self.client.post('/initialize',
                                      data=json.dumps({"difficulty": "easy"}),
                                      content_type='application/json')
        self.init_data = init_response.get_json()
        self.assertEqual(init_response.status_code, 200, "Initialize should succeed")
        
        # Print the initial board state
        print("Initial board received from /initialize:")
        print(json.dumps(self.init_data.get('board', {}), indent=2))
    
    def test_direct_e2_to_e4_move(self):
        """Test a direct move from e2 to e4 via the /move endpoint."""
        # Make the move
        move_response = self.client.post('/move',
                                      data=json.dumps({"from": "e2", "to": "e4"}),
                                      content_type='application/json')
        
        self.assertEqual(move_response.status_code, 200, "Move should succeed")
        
        move_data = move_response.get_json()
        
        # Print the move response
        print("\nMove response from e2 to e4:")
        print(json.dumps(move_data, indent=2))
        
        # Check if the move was valid according to the response
        self.assertTrue(move_data.get('valid', False), "Move should be indicated as valid")
        
        # Check if the piece has moved
        board = move_data.get('board', {})
        self.assertIn('e4', board, "Board should have a piece at e4 after the move")
        self.assertNotIn('e2', board, "Board should not have a piece at e2 after the move")
        
        # Check the piece type and color
        e4_piece = board.get('e4', {})
        self.assertEqual(e4_piece.get('color'), 'white', "Piece at e4 should be white")
        self.assertIn(e4_piece.get('type'), ['p', 'pawn'], "Piece at e4 should be a pawn")
    
    def test_initialize_then_move(self):
        """Test the full flow - initialize game, then make a move."""
        # Re-initialize the game to ensure a clean state
        init_response = self.client.post('/initialize',
                                      data=json.dumps({"difficulty": "easy"}),
                                      content_type='application/json')
        init_data = init_response.get_json()
        
        # Verify the initial state has a piece at e2
        self.assertIn('e2', init_data.get('board', {}), "Initial board should have a piece at e2")
        
        # Make the move
        move_response = self.client.post('/move',
                                      data=json.dumps({"from": "e2", "to": "e4"}),
                                      content_type='application/json')
        move_data = move_response.get_json()
        
        # Print both responses for debugging
        print("\nInitialize data:")
        print(json.dumps(init_data, indent=2))
        print("\nMove data:")
        print(json.dumps(move_data, indent=2))
        
        # Check if the move was successful
        self.assertTrue(move_data.get('valid', False), "Move should be valid")
        
        # Check if piece moved from e2 to e4
        board_after_move = move_data.get('board', {})
        self.assertIn('e4', board_after_move, "Board should have a piece at e4 after the move")
        self.assertNotIn('e2', board_after_move, "Board should not have a piece at e2 after the move")
    
    def test_actual_http_request(self):
        """Send an actual HTTP request to the server if it's running."""
        try:
            # Try to connect to the server running on port 5001
            server_url = "http://localhost:5001"
            
            # First initialize the game
            init_response = requests.post(
                f"{server_url}/initialize",
                json={"difficulty": "easy"},
                timeout=2  # 2 second timeout
            )
            
            if init_response.status_code == 200:
                print("\nSuccessfully initialized game on live server")
                
                # Make a move
                move_response = requests.post(
                    f"{server_url}/move",
                    json={"from": "e2", "to": "e4"},
                    timeout=2  # 2 second timeout
                )
                
                if move_response.status_code == 200:
                    move_data = move_response.json()
                    print("\nSuccessfully made move on live server")
                    print(json.dumps(move_data, indent=2))
                    
                    # Check if the piece moved
                    self.assertTrue(move_data.get('valid', False), "Move should be valid")
                    
                    # Check e4 and e2 in returned board
                    board = move_data.get('board', {})
                    self.assertIn('e4', board, "Board should have a piece at e4")
                    self.assertNotIn('e2', board, "Board should not have a piece at e2")
                else:
                    print(f"\nFailed to make move on live server: {move_response.status_code}")
            else:
                print(f"\nFailed to initialize game on live server: {init_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"\nCould not connect to server: {e}")
            print("Skipping live server test")
            return  # Skip the test if server is not running

if __name__ == '__main__':
    unittest.main() 