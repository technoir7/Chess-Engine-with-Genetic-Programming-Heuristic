import unittest
import json
import sys
import os

# Add the parent directory to the path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, board_to_dict
from chess_logic_by_thomasahle import Position, initial

class TestPieceMovementFix(unittest.TestCase):
    
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
    
    def test_move_white_pawn(self):
        """Test that a white pawn can move forward one square.

        board_to_dict returns single-letter type codes ('p' not 'pawn').
        """
        move_response = self.client.post('/move',
                                        data=json.dumps({"from": "e2", "to": "e3"}),
                                        content_type='application/json')
        move_data = move_response.get_json()

        self.assertTrue(move_data.get('valid', False), "Pawn move should be valid")

        board = move_data.get('board', {})
        self.assertIn('e3', board, "Pawn should be moved to e3")
        self.assertNotIn('e2', board, "Pawn should no longer be at e2")

        piece = board.get('e3', {})
        self.assertEqual(piece.get('type'), 'p', "Piece type should be 'p' (pawn)")
        self.assertEqual(piece.get('color'), 'white', "Piece should be white")
    
    def test_move_white_pawn_two_squares(self):
        """Test that a white pawn can move forward two squares from its starting position."""
        # Make a valid pawn move from e2 to e4
        move_response = self.client.post('/move',
                                        data=json.dumps({"from": "e2", "to": "e4"}),
                                        content_type='application/json')
        move_data = move_response.get_json()
        
        # Verify the move was successful
        self.assertTrue(move_data.get('valid', False), "Pawn two-square move should be valid")
        
        # Check if the board was updated correctly
        board = move_data.get('board', {})
        self.assertIn('e4', board, "Pawn should be moved to e4")
        self.assertNotIn('e2', board, "Pawn should no longer be at e2")
    
    def test_move_white_knight(self):
        """Test that a white knight can move in its L-shape pattern.

        board_to_dict returns single-letter type codes ('n' not 'knight').
        """
        move_response = self.client.post('/move',
                                        data=json.dumps({"from": "g1", "to": "f3"}),
                                        content_type='application/json')
        move_data = move_response.get_json()

        self.assertTrue(move_data.get('valid', False), "Knight move should be valid")

        board = move_data.get('board', {})
        self.assertIn('f3', board, "Knight should be moved to f3")
        self.assertNotIn('g1', board, "Knight should no longer be at g1")

        piece = board.get('f3', {})
        self.assertEqual(piece.get('type'), 'n', "Piece type should be 'n' (knight)")
        self.assertEqual(piece.get('color'), 'white', "Piece should be white")
    
    def test_move_sequence_multiple_pieces(self):
        """Test a sequence of different piece movements to ensure continuity."""
        # 1. Move pawn e2 to e4
        move1 = self.client.post('/move',
                                data=json.dumps({"from": "e2", "to": "e4"}),
                                content_type='application/json')
        data1 = move1.get_json()
        self.assertTrue(data1.get('valid', False), "First move should be valid")
        
        # 2. Move knight from g1 to f3
        move2 = self.client.post('/move',
                                data=json.dumps({"from": "g1", "to": "f3"}),
                                content_type='application/json')
        data2 = move2.get_json()
        self.assertTrue(data2.get('valid', False), "Second move should be valid")
        
        # 3. Move bishop from f1 to c4
        move3 = self.client.post('/move',
                                data=json.dumps({"from": "f1", "to": "c4"}),
                                content_type='application/json')
        data3 = move3.get_json()
        self.assertTrue(data3.get('valid', False), "Third move should be valid")
        
        # Check final board state
        board = data3.get('board', {})
        self.assertIn('e4', board, "Pawn should be at e4")
        self.assertIn('f3', board, "Knight should be at f3")
        self.assertIn('c4', board, "Bishop should be at c4")
        
        # board_to_dict uses single-letter codes: 'p'=pawn, 'n'=knight, 'b'=bishop
        self.assertEqual(board.get('e4', {}).get('type'), 'p', "Piece at e4 should be a pawn (type='p')")
        self.assertEqual(board.get('f3', {}).get('type'), 'n', "Piece at f3 should be a knight (type='n')")
        self.assertEqual(board.get('c4', {}).get('type'), 'b', "Piece at c4 should be a bishop (type='b')")
    
    def test_coordinate_conversion(self):
        """Test that coordinate conversion between algebraic and internal works correctly."""
        from app import square_to_coord, coord_to_square
        
        # Test some common square to coord conversions
        self.assertEqual(square_to_coord('e2'), 85, "e2 should convert to internal coordinate 85")
        self.assertEqual(square_to_coord('a1'), 91, "a1 should convert to internal coordinate 91")
        self.assertEqual(square_to_coord('h8'), 28, "h8 should convert to internal coordinate 28")
        
        # Test the reverse conversions
        self.assertEqual(coord_to_square(85), 'e2', "Internal coordinate 85 should convert to e2")
        self.assertEqual(coord_to_square(91), 'a1', "Internal coordinate 91 should convert to a1")
        self.assertEqual(coord_to_square(28), 'h8', "Internal coordinate 28 should convert to h8")
    
    def test_valid_moves_generation(self):
        """Test that valid moves are generated correctly for pieces."""
        # Create a fresh position
        position = Position(initial, 0, (True, True), (True, True), 0, 0)
        
        # Generate all valid moves for this position
        valid_moves = list(position.gen_moves())
        
        # Test that some expected initial moves are in the valid moves list
        # Converting to algebraic notation for readability in tests
        from app import coord_to_square
        
        algebraic_moves = [(coord_to_square(m[0]), coord_to_square(m[1])) for m in valid_moves]
        
        # Check if standard opening moves are available
        self.assertIn(('e2', 'e4'), algebraic_moves, "Pawn e2-e4 should be a valid move")
        self.assertIn(('e2', 'e3'), algebraic_moves, "Pawn e2-e3 should be a valid move")
        self.assertIn(('g1', 'f3'), algebraic_moves, "Knight g1-f3 should be a valid move")
        self.assertIn(('b1', 'c3'), algebraic_moves, "Knight b1-c3 should be a valid move")
    
    def test_move_results_in_board_update(self):
        """Test that when a piece moves, the board state is correctly updated."""
        # Get initial board state
        response = self.client.post('/initialize',
                                  data=json.dumps({"difficulty": "easy"}),
                                  content_type='application/json')
        init_board = response.get_json().get('board', {})
        
        # Make a move (e2 to e4)
        move_response = self.client.post('/move',
                                        json={"from": "e2", "to": "e4"},
                                        content_type='application/json')
        move_data = move_response.get_json()
        
        # Get updated board state
        updated_board = move_data.get('board', {})
        
        # Verify the differences between initial and updated board
        self.assertNotEqual(init_board, updated_board, "Board should be updated after move")
        self.assertIn('e4', updated_board, "New position should be in updated board")
        self.assertNotIn('e2', updated_board, "Old position should not be in updated board")
        
        # Find all squares that have changed
        removed_squares = set(init_board.keys()) - set(updated_board.keys())
        added_squares = set(updated_board.keys()) - set(init_board.keys())
        
        # Player move: e2 to e4
        expected_removed = {'e2'}
        expected_added = {'e4'}
        
        # Check for AI move: look for a black piece that moved
        ai_from = None
        ai_to = None
        
        # Try to identify AI's actual move by finding the black pieces that changed
        for square in removed_squares:
            piece = init_board.get(square, {})
            if piece.get('color') == 'black':
                ai_from = square
                break
                
        for square in added_squares:
            piece = updated_board.get(square, {})
            if piece.get('color') == 'black' and square not in init_board:
                ai_to = square
                break
                
        # If we found an AI move, add it to expected changes
        if ai_from and ai_to:
            print(f"Detected AI move: {ai_from}-{ai_to}")
            expected_removed.add(ai_from)
            expected_added.add(ai_to)
            
        # Verify only expected squares have changed
        unexpected_removed = removed_squares - expected_removed
        unexpected_added = added_squares - expected_added
        
        if unexpected_removed or unexpected_added:
            self.fail(f"Unexpected board changes - Removed: {unexpected_removed}, Added: {unexpected_added}")
    
    def test_internal_move_mechanism(self):
        """Test the internal move mechanism of the Position class."""
        # Create a fresh position
        position = Position(initial, 0, (True, True), (True, True), 0, 0)
        
        # Convert algebraic to internal coordinates
        from app import square_to_coord
        e2 = square_to_coord('e2')
        e4 = square_to_coord('e4')
        
        # Make the move directly using the Position.move() method
        new_position = position.move((e2, e4))
        
        # Since the position is rotated after a move, we need to rotate it back for comparison
        new_position = new_position.rotate()
        
        # Check that the pawn has moved
        self.assertEqual(new_position.board[e4], 'P', "Pawn should be at e4")
        self.assertEqual(new_position.board[e2], '.', "Original square should be empty")
    
    def test_move_history_tracking(self):
        """Test that moves are correctly tracked in the move history."""
        # Make a move
        move_response = self.client.post('/move',
                                        data=json.dumps({"from": "e2", "to": "e4"}),
                                        content_type='application/json')
        move_data = move_response.get_json()
        
        # Check that the move is recorded in the move history
        moves = move_data.get('moves', [])
        self.assertGreaterEqual(len(moves), 1, "Move history should contain at least one move")
        
        # Find the player's move in the history
        player_moves = [m for m in moves if m.get('player') == 'white']
        self.assertGreaterEqual(len(player_moves), 1, "Move history should contain the player's move")
        
        # Check that the move details are correct
        last_player_move = player_moves[-1]
        self.assertEqual(last_player_move.get('from'), 'e2', "Move should be from e2")
        self.assertEqual(last_player_move.get('to'), 'e4', "Move should be to e4")

if __name__ == '__main__':
    unittest.main() 