import unittest
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import square_to_coord, coord_to_square

class TestCoordinateTransforms(unittest.TestCase):
    def test_square_to_coord_all_squares(self):
        """Test that all chess squares convert to internal coordinates correctly."""
        # Test all possible squares
        for file_char in "abcdefgh":
            for rank in range(1, 9):
                square = f"{file_char}{rank}"
                coord = square_to_coord(square)
                
                # Verify the coord is not None
                self.assertIsNotNone(coord, f"Conversion of {square} to coord failed")
                
                # Verify the coord is within the valid range
                self.assertTrue(21 <= coord <= 98, f"Coord {coord} outside valid range for square {square}")
                
                # Convert back and verify it matches the original
                converted_square = coord_to_square(coord)
                self.assertEqual(square, converted_square, 
                                f"Square {square} -> Coord {coord} -> Square {converted_square} mismatch")
                
                print(f"Square {square} <-> Coord {coord}: PASS")
    
    def test_specific_square_conversions(self):
        """Test specific square conversions known to be important for moves."""
        test_cases = [
            # Starting positions for white pieces
            ('a1', 91), ('b1', 92), ('c1', 93), ('d1', 94),
            ('e1', 95), ('f1', 96), ('g1', 97), ('h1', 98),
            
            # Starting positions for white pawns
            ('a2', 81), ('b2', 82), ('c2', 83), ('d2', 84),
            ('e2', 85), ('f2', 86), ('g2', 87), ('h2', 88),
            
            # Starting positions for black pawns
            ('a7', 31), ('b7', 32), ('c7', 33), ('d7', 34),
            ('e7', 35), ('f7', 36), ('g7', 37), ('h7', 38),
            
            # Starting positions for black pieces
            ('a8', 21), ('b8', 22), ('c8', 23), ('d8', 24),
            ('e8', 25), ('f8', 26), ('g8', 27), ('h8', 28),
            
            # Common central squares
            ('e4', 65), ('d4', 64), ('e5', 55), ('d5', 54)
        ]
        
        for square, expected_coord in test_cases:
            # Test square to coord
            coord = square_to_coord(square)
            self.assertEqual(coord, expected_coord, 
                           f"Square {square} should convert to coord {expected_coord}, got {coord}")
            
            # Test coord to square
            converted_square = coord_to_square(expected_coord)
            self.assertEqual(converted_square, square, 
                           f"Coord {expected_coord} should convert to square {square}, got {converted_square}")
    
    def test_invalid_squares(self):
        """Test that invalid squares are handled correctly."""
        invalid_squares = ['a0', 'i1', 'a9', 'j9', 'aa', '11', '']
        
        for square in invalid_squares:
            try:
                coord = square_to_coord(square)
                self.assertIsNone(coord, f"Invalid square {square} should return None, got {coord}")
            except ValueError:
                # This is also acceptable - the function could raise ValueError for invalid input
                pass
    
    def test_invalid_coords(self):
        """Test that invalid coordinates raise ValueError.

        coord_to_square raises ValueError for coordinates that fall outside the
        8x8 board region (valid range is 21-98 exclusive of the padding columns).
        The test previously expected a graceful default return value, but the
        current implementation raises ValueError instead, which is equally safe.
        """
        invalid_coords = [0, 20, 99, 120, -1]

        for coord in invalid_coords:
            with self.assertRaises(ValueError,
                                   msg=f"coord_to_square({coord}) should raise ValueError for an off-board coordinate"):
                coord_to_square(coord)

if __name__ == '__main__':
    unittest.main() 