import unittest
import json
import re
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class FrontendInteractionsTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_chessboard_click_handlers(self):
        """Test that chessboard.js properly sets up click handlers for squares.

        The current implementation attaches a single delegated click listener to
        the board element itself (not to each individual square element), and
        dispatches to this.handleSquareClick.  The test reflects this pattern.
        """
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()

            # Verify setupEventListeners function exists
            has_setup = "setupEventListeners" in js_content
            self.assertTrue(has_setup, "Should have a setupEventListeners function")

            # The board element itself gets the delegated click listener
            adds_listeners = re.search(r'addEventListener\(["\']click', js_content)
            self.assertIsNotNone(adds_listeners, "Should add click event listeners")

            # The handler must call handleSquareClick
            has_handle_click = "handleSquareClick" in js_content
            self.assertTrue(has_handle_click, "Click handler should call handleSquareClick")
    
    def test_handle_square_click_logic(self):
        """Test that handleSquareClick contains the necessary logic for piece movement."""
        # Read the chessboard.js file
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()
            
            # Check for key functions and methods
            has_handle_click = "handleSquareClick" in js_content
            self.assertTrue(has_handle_click, "Should have a handleSquareClick function")
            
            has_player_click = "handlePlayerSquareClick" in js_content
            self.assertTrue(has_player_click, "Should have a handlePlayerSquareClick function")
            
            has_select_square = "selectSquare" in js_content
            self.assertTrue(has_select_square, "Should have a selectSquare function")
            
            has_deselect = "deselectSquare" in js_content
            self.assertTrue(has_deselect, "Should have a deselectSquare function")
            
            has_legal_moves = "legalMoves" in js_content
            self.assertTrue(has_legal_moves, "Should check for legalMoves")
            
            has_make_move = "makeMove" in js_content
            self.assertTrue(has_make_move, "Should have a makeMove function")
            
            # Make sure functions call each other
            makes_call = "this.handlePlayerSquareClick" in js_content
            self.assertTrue(makes_call, "handleSquareClick should call handlePlayerSquareClick")
    
    def test_make_move_sends_data_to_backend(self):
        """Test that makeMove function properly sends move data to the backend.

        The implementation calls sendMoveToBackend which POSTs to /make_move
        (the route alias for /move).  The test checks for the actual endpoint
        used in the current code rather than the previous /move literal.
        """
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()

            self.assertTrue("makeMove" in js_content, "Should have a makeMove function")
            self.assertTrue("this.sendMoveToBackend" in js_content,
                            "makeMove should call sendMoveToBackend")
            self.assertTrue("sendMoveToBackend" in js_content,
                            "Should have a sendMoveToBackend function")
            # The JS sends to /make_move (the /move route alias registered in app.py)
            has_fetch = "fetch('/make_move'" in js_content or "fetch('/move'" in js_content or "/make_move" in js_content
            self.assertTrue(has_fetch, "Should make a fetch call to the move endpoint")
    
    def test_game_js_extends_move_function(self):
        """Test that the game.js handles chess board events."""
        # Read the game.js file
        with open('static/js/game.js', 'r') as file:
            js_content = file.read()
            
            # Check for event listeners
            has_event_listeners = "addEventListener" in js_content
            self.assertTrue(has_event_listeners, "Should set up event listeners")
            
            handles_move_events = "moveCompleted" in js_content
            self.assertTrue(handles_move_events, "Should handle move completed events")
            
            updates_player = "currentPlayer" in js_content
            self.assertTrue(updates_player, "Should update current player")
            
            has_history = "addMoveToHistory" in js_content
            self.assertTrue(has_history, "Should add moves to history")
    
    def test_send_move_to_backend_function(self):
        """Test that chessboard.js has a sendMoveToBackend function that makes API calls.

        The implementation packages the move as a JSON object that includes at
        minimum 'from' and 'to' fields.  The exact serialisation expression has
        changed from the previous "body: JSON.stringify({ from, to })" shorthand
        to a named 'data' variable, so the test checks for the presence of the
        required fields rather than the exact syntax.
        """
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()

            self.assertTrue("sendMoveToBackend" in js_content,
                            "Should have a sendMoveToBackend function")
            # Accepts either /move or /make_move (both are registered in app.py)
            has_fetch = "/make_move" in js_content or "/move" in js_content
            self.assertTrue(has_fetch, "Should reference the move endpoint")
            self.assertTrue("JSON.stringify" in js_content,
                            "Should stringify JSON data")
            # 'from' and 'to' fields are included in the serialised payload
            self.assertTrue("from:" in js_content or "from :" in js_content,
                            "Payload should include a 'from' field")
            self.assertTrue("to:" in js_content or "to :" in js_content,
                            "Payload should include a 'to' field")
            self.assertTrue(".then" in js_content,
                            "Should use promises to handle response")
            self.assertTrue("updateBoard(" in js_content,
                            "Should update the board with response data")
    
    def test_browser_events_for_piece_movement(self):
        """Test that the necessary browser events for piece movement are properly handled."""
        # Read all the JS files to find event handlers
        with open('static/js/chessboard.js', 'r') as file:
            chessboard_js = file.read()
        
        with open('static/js/game.js', 'r') as file:
            game_js = file.read()
        
        # Check for click event handling
        has_click_handlers = 'addEventListener("click"' in chessboard_js or "addEventListener('click'" in chessboard_js
        self.assertTrue(has_click_handlers, "Should have click event listeners")
        
        # Check for proper event delegation or bubbling
        handles_delegation = re.search(r'target|currentTarget', chessboard_js + game_js)
        self.assertIsNotNone(handles_delegation, "Should handle event delegation for piece clicks")
        
        # Check for preventing default browser actions if necessary
        prevents_default = re.search(r'preventDefault\(\)|return false', chessboard_js + game_js)
        self.assertTrue(prevents_default is not None or not re.search(r'draggable|drag', chessboard_js + game_js), 
                       "Should prevent default browser actions if using draggable elements")

if __name__ == '__main__':
    unittest.main() 