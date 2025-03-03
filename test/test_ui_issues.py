import unittest
import json
import re
import os
from bs4 import BeautifulSoup
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class UIIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_pieces_displayed_as_images(self):
        """Test that chess pieces are displayed as images, not as text."""
        # Get the index page to check the HTML structure
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check the JS files referenced - there should be a chessboard.js that handles rendering
        scripts = soup.find_all('script')
        js_files = [script.get('src') for script in scripts if script.get('src')]
        
        # Verify the required JS files are loaded
        self.assertTrue(any('/static/js/chessboard.js' in js for js in js_files), 
                       "chessboard.js must be loaded for proper chess piece rendering")
        self.assertTrue(any('/static/js/game.js' in js for js in js_files),
                       "game.js must be loaded for game interaction")
        
        # Check if there are image paths defined in the CSS or JS
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()
            # Check for image paths in the JS
            has_image_paths = re.search(r'pieces\/.*\.svg', js_content) is not None
            self.assertTrue(has_image_paths, "Chess piece image paths should be defined in chessboard.js")

    def test_api_returns_proper_piece_info(self):
        """Test that the API returns proper piece information for the UI to render pieces correctly."""
        # Initialize a new game
        init_response = self.client.post('/initialize',
                                        data='{"difficulty": "easy"}',
                                        content_type='application/json')
        
        init_data = init_response.get_json()
        board = init_data['board']
        
        # Check that the board is returned
        self.assertIsNotNone(board, "Board should be returned in the API response")
        self.assertGreater(len(board), 0, "Board should contain pieces")
        
        # Check that pieces have the correct properties for the UI to render images
        for square, piece in board.items():
            self.assertIn('type', piece, f"Piece at {square} should have a 'type' property")
            self.assertIn('color', piece, f"Piece at {square} should have a 'color' property")
            
            # Check that piece type is one of the standard chess piece types
            self.assertIn(piece['type'], ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king'],
                         f"Piece type at {square} should be a standard chess piece type")
            
            # Check that piece color is either white or black
            self.assertIn(piece['color'], ['white', 'black'],
                         f"Piece color at {square} should be either white or black")
    
    def test_chessboard_uses_images_not_text(self):
        """Test that the chessboard.js file is configured to use SVG images rather than text."""
        # Read the chessboard.js file to analyze its configuration
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()
            
            # Check if there's a pieceImages object/mapping
            has_piece_images_map = re.search(r'pieceImages\s*=\s*{', js_content) is not None
            self.assertTrue(has_piece_images_map, 
                           "chessboard.js should have a pieceImages mapping to render pieces as images")
            
            # Check that the placePiece function creates img elements
            creates_img_elements = re.search(r'document\.createElement\([\'"]img[\'"]\)', js_content) is not None
            self.assertTrue(creates_img_elements, 
                           "The placePiece function should create img elements for pieces")
            
            # Check it's not just using textContent to display piece names
            doesnt_use_textContent = re.search(r'\.textContent\s*=\s*(pieceColor|pieceType)', js_content) is None
            self.assertTrue(doesnt_use_textContent, 
                           "The chess pieces should not be rendered as text via textContent")

    def test_no_literal_piece_text_displayed(self):
        """Test that pieces aren't displayed as literal text like 'white pawn'."""
        # Read the chessboard.js file to look for problematic code
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()
            
            # Check for any code that might concatenate color and type for display
            text_rendering_pattern = re.search(r'\.textContent\s*=\s*(.*color.*type|.*type.*color)', js_content)
            self.assertIsNone(text_rendering_pattern, "Pieces should not be rendered by setting textContent to color + type")
            
            # Check the placePiece function for proper SVG handling
            piece_display_code = re.findall(r'placePiece\s*\([^\)]*\)\s*{[^}]*}', js_content, re.DOTALL)
            self.assertTrue(piece_display_code, "The placePiece function should be defined")
            
            # Check that the placePiece function doesn't set innerHTML or textContent to piece description
            for code in piece_display_code:
                doesnt_use_text = not re.search(r'\.(?:innerHTML|textContent)\s*=\s*.*\+.*', code)
                self.assertTrue(doesnt_use_text, "The placePiece function should not set text content to piece descriptions")
            
            # Check that SVG images are created and used
            creates_svg_img = re.search(r'createElement\([\'"]img[\'"]\).*\.src\s*=', js_content, re.DOTALL) is not None
            self.assertTrue(creates_svg_img, "Should create img elements and set their source to SVG files")
    
    def test_pieces_are_movable(self):
        """Test that chess pieces have click handlers and can be moved."""
        # Read the chessboard.js to check for event handlers
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()
            
            # Check for event listeners on squares
            has_click_handlers = re.search(r'addEventListener\([\'"]click[\'"]', js_content) is not None
            self.assertTrue(has_click_handlers, "Squares should have click event listeners for piece movement")
            
            # Check for handleSquareClick function
            has_handle_click = re.search(r'handleSquareClick\s*\(', js_content) is not None
            self.assertTrue(has_handle_click, "There should be a handleSquareClick function to process clicks")
            
            # Check that selectedSquare state is tracked for move origin
            tracks_selected = re.search(r'selectedSquare\s*=', js_content) is not None
            self.assertTrue(tracks_selected, "The code should track the selected square for moves")
            
            # Check for makeMove function that handles actual piece movement
            has_make_move = re.search(r'makeMove\s*\([^\)]*\)', js_content) is not None
            self.assertTrue(has_make_move, "There should be a makeMove function to execute piece movements")

    def test_svg_files_exist(self):
        """Test that all required SVG files for chess pieces exist and are accessible."""
        # Get the piece image paths from chessboard.js
        with open('static/js/chessboard.js', 'r') as file:
            js_content = file.read()
            
            # Extract all SVG file paths mentioned in the JS
            svg_paths = re.findall(r'[\'"](/static/images/pieces/[^\'"]*.svg)[\'"]', js_content)
            self.assertTrue(svg_paths, "Should find SVG file paths in chessboard.js")
            
            # Check if each SVG file exists in the filesystem
            for svg_path in svg_paths:
                # Remove leading slash to get the relative path
                relative_path = svg_path[1:] if svg_path.startswith('/') else svg_path
                
                # Check if the file exists
                file_exists = os.path.isfile(relative_path)
                self.assertTrue(file_exists, f"SVG file {relative_path} should exist")
                
                # Check if the file is non-empty
                file_size = os.path.getsize(relative_path) if file_exists else 0
                self.assertGreater(file_size, 0, f"SVG file {relative_path} should have content")
                
                # Open and check if it's a valid SVG
                if file_exists:
                    with open(relative_path, 'r') as svg_file:
                        svg_content = svg_file.read()
                        is_svg = '<svg' in svg_content.lower()
                        self.assertTrue(is_svg, f"File {relative_path} should be a valid SVG")

if __name__ == '__main__':
    unittest.main() 