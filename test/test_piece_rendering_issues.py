import unittest
import json
from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class PieceRenderingIssuesTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize app."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_all_pieces_present_on_initial_board(self):
        """Test that all 32 pieces (16 white, 16 black) are present on the initial board."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Verify all 32 pieces are present
        self.assertEqual(len(init_board), 32, "Board should have 32 pieces total")
        
        # Count white and black pieces
        white_pieces = 0
        black_pieces = 0
        
        for square, piece in init_board.items():
            if piece['color'] == 'white':
                white_pieces += 1
            elif piece['color'] == 'black':
                black_pieces += 1
                
        self.assertEqual(white_pieces, 16, "Board should have 16 white pieces")
        self.assertEqual(black_pieces, 16, "Board should have 16 black pieces")
        
        # Verify specific pieces
        self._verify_starting_piece(init_board, 'a1', 'r', 'white', "White rook missing from a1")
        self._verify_starting_piece(init_board, 'b1', 'n', 'white', "White knight missing from b1")
        self._verify_starting_piece(init_board, 'c1', 'b', 'white', "White bishop missing from c1")
        self._verify_starting_piece(init_board, 'd1', 'q', 'white', "White queen missing from d1")
        self._verify_starting_piece(init_board, 'e1', 'k', 'white', "White king missing from e1")
        self._verify_starting_piece(init_board, 'f1', 'b', 'white', "White bishop missing from f1")
        self._verify_starting_piece(init_board, 'g1', 'n', 'white', "White knight missing from g1")
        self._verify_starting_piece(init_board, 'h1', 'r', 'white', "White rook missing from h1")
        
        # Check white pawns
        for file_char in 'abcdefgh':
            square = f"{file_char}2"
            self._verify_starting_piece(init_board, square, 'p', 'white', f"White pawn missing from {square}")
        
        # Check black pieces
        self._verify_starting_piece(init_board, 'a8', 'r', 'black', "Black rook missing from a8")
        self._verify_starting_piece(init_board, 'b8', 'n', 'black', "Black knight missing from b8")
        self._verify_starting_piece(init_board, 'c8', 'b', 'black', "Black bishop missing from c8")
        self._verify_starting_piece(init_board, 'd8', 'q', 'black', "Black queen missing from d8")
        self._verify_starting_piece(init_board, 'e8', 'k', 'black', "Black king missing from e8")
        self._verify_starting_piece(init_board, 'f8', 'b', 'black', "Black bishop missing from f8")
        self._verify_starting_piece(init_board, 'g8', 'n', 'black', "Black knight missing from g8")
        self._verify_starting_piece(init_board, 'h8', 'r', 'black', "Black rook missing from h8")
        
        # Check black pawns
        for file_char in 'abcdefgh':
            square = f"{file_char}7"
            self._verify_starting_piece(init_board, square, 'p', 'black', f"Black pawn missing from {square}")
            
    def test_no_white_text_on_board(self):
        """Test that there's no raw 'white' text appearing incorrectly on the board."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        init_data = init_response.get_json()
        init_board = init_data['board']
        
        # Check that no raw "white" text appears incorrectly
        self._check_no_raw_white_text(init_board)
        
        # Make a few moves to test if the issue appears after board updates
        moves = [
            ('e2', 'e4'),  # White pawn
            ('e7', 'e5'),  # Black pawn
            ('g1', 'f3'),  # White knight
        ]
        
        for from_square, to_square in moves:
            move_response = self.client.post('/move',
                                   data=json.dumps({"from": from_square, "to": to_square}),
                                   content_type='application/json')
            move_data = move_response.get_json()
            board = move_data['board']
            
            # Check that no "white" text appears incorrectly after each move
            self._check_no_raw_white_text(board)
            
    def test_correct_piece_colors_after_moves(self):
        """Test that pieces maintain their correct colors after multiple moves."""
        # Initialize the game
        init_response = self.client.post('/initialize',
                                   data='{"difficulty": "easy"}',
                                   content_type='application/json')
        
        # Make a series of moves that might expose color issues
        moves = [
            ('e2', 'e4'),  # White pawn
            ('e7', 'e5'),  # Black pawn
            ('f1', 'c4'),  # White bishop
            ('b8', 'c6'),  # Black knight
            ('d1', 'h5'),  # White queen
            ('g8', 'f6'),  # Black knight
        ]
        
        board = init_response.get_json()['board']
        
        # Track the source squares to verify pieces have moved
        moved_pieces = {}
        
        for move_num, (from_square, to_square) in enumerate(moves, 1):
            # Keep track of what was at the from_square before the move
            if from_square in board:
                moved_pieces[from_square] = {
                    'destination': to_square,
                    'type': board[from_square]['type'],
                    'color': board[from_square]['color']
                }
            
            # Make the move
            move_response = self.client.post('/move',
                                   data=json.dumps({"from": from_square, "to": to_square}),
                                   content_type='application/json')
            move_data = move_response.get_json()
            
            # Skip the move if it was invalid (this can happen in the test, especially with black moves)
            if 'error' in move_data or (move_data.get('valid') == False):
                print(f"Skipping invalid move {from_square}-{to_square}: {move_data.get('message', move_data.get('error', 'Unknown error'))}")
                continue
                
            board = move_data['board']
            
            # Count pieces by color and type after each move
            self._verify_piece_counts_by_color(board, move_num)
            
            # Specifically check the moved piece has the correct color
            # But only if it was a valid move and the destination square should have the piece
            expected_color = 'white' if move_num % 2 != 0 else 'black'
            
            # Check if the piece has actually moved to the destination square
            if to_square in board:
                self._verify_piece_color(board, to_square, expected_color)
                
                # Also verify it's the right type of piece
                if from_square in moved_pieces:
                    expected_type = moved_pieces[from_square]['type']
                    piece = board[to_square]
                    self.assertEqual(piece['type'], expected_type, 
                                    f"Wrong piece type at {to_square}. Expected {expected_type}, got {piece['type']}")
    
    def _verify_starting_piece(self, board, square, expected_type, expected_color, message):
        """Verify a piece is at the expected square with correct type and color."""
        self.assertIn(square, board, f"No piece at {square}")
        piece = board[square]
        self.assertEqual(piece['type'], expected_type, 
                       f"Wrong piece type at {square}. Expected {expected_type}, got {piece['type']}")
        self.assertEqual(piece['color'], expected_color, 
                       f"Wrong piece color at {square}. Expected {expected_color}, got {piece['color']}")
    
    def _check_no_raw_white_text(self, board):
        """Helper method to check that no raw 'white' text appears in the wrong place."""
        for square, piece in board.items():
            # Check if this is a white piece
            is_white_piece = piece['color'] == 'white'
            
            # For pieces that aren't white, 'white' should never appear in any property
            if not is_white_piece:
                piece_json = json.dumps(piece)
                self.assertNotIn('white', piece_json.lower(), 
                              f"Found 'white' text in non-white piece at {square}: {piece}")
            
            # For white pieces, 'white' should only appear as the value of the 'color' property
            if is_white_piece:
                # Convert to JSON and count occurrences of "white"
                piece_json = json.dumps(piece)
                occurrences = piece_json.lower().count('white')
                self.assertEqual(occurrences, 1, 
                               f"Found multiple instances of 'white' in piece at {square}: {piece}")
    
    def _verify_piece_counts_by_color(self, board, move_number):
        """Verify the correct number of pieces by color after a given move number."""
        # Count white and black pieces
        white_pieces = 0
        black_pieces = 0
        
        for square, piece in board.items():
            if piece['color'] == 'white':
                white_pieces += 1
            elif piece['color'] == 'black':
                black_pieces += 1
                
        # In the first few moves, we shouldn't have any captures, so counts should stay at 16 each
        if move_number <= 6:  # For the 6 moves in our test
            self.assertEqual(white_pieces, 16, f"After move {move_number}, should have 16 white pieces")
            self.assertEqual(black_pieces, 16, f"After move {move_number}, should have 16 black pieces")
            
    def _verify_piece_color(self, board, square, expected_color):
        """Verify a piece at the given square has the expected color."""
        self.assertIn(square, board, f"No piece at {square}")
        piece = board[square]
        self.assertEqual(piece['color'], expected_color, 
                       f"Wrong piece color at {square}. Expected {expected_color}, got {piece['color']}")

if __name__ == '__main__':
    unittest.main() 