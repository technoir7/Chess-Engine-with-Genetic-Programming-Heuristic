#!/usr/bin/env python3
"""
Simplified test script to check the coordinate conversion functions.
"""

from app import square_to_coord, coord_to_square
from chess_logic_by_thomasahle import A1, H1, A8, H8

def test_square_to_coord():
    print("Testing square_to_coord:")
    
    # Test key coordinates
    test_squares = [
        ('a1', A1),  # A1 = 91
        ('h1', H1),  # H1 = 98
        ('a8', A8),  # A8 = 21
        ('h8', H8),  # H8 = 28
        ('e2', 85),  # e2 should be 85
        ('e4', 65),  # e4 should be 65
        ('d5', 54),  # d5 should be 54
    ]
    
    passed = 0
    for square, expected in test_squares:
        try:
            result = square_to_coord(square)
            if result == expected:
                print(f"✓ {square} -> {result} (Expected: {expected})")
                passed += 1
            else:
                print(f"✗ {square} -> {result} (Expected: {expected})")
        except Exception as e:
            print(f"✗ {square} -> Error: {e}")
    
    print(f"Passed {passed}/{len(test_squares)} tests\n")

def test_coord_to_square():
    print("Testing coord_to_square:")
    
    # Test key coordinates
    test_coords = [
        (A1, 'a1'),  # A1 = 91
        (H1, 'h1'),  # H1 = 98
        (A8, 'a8'),  # A8 = 21
        (H8, 'h8'),  # H8 = 28
        (85, 'e2'),  # 85 should be e2
        (65, 'e4'),  # 65 should be e4
        (54, 'd5'),  # 54 should be d5
    ]
    
    passed = 0
    for coord, expected in test_coords:
        try:
            result = coord_to_square(coord)
            if result == expected:
                print(f"✓ {coord} -> {result} (Expected: {expected})")
                passed += 1
            else:
                print(f"✗ {coord} -> {result} (Expected: {expected})")
        except Exception as e:
            print(f"✗ {coord} -> Error: {e}")
    
    print(f"Passed {passed}/{len(test_coords)} tests\n")

def test_round_trip():
    print("Testing round trip conversions:")
    
    # Test squares
    test_squares = ['a1', 'h1', 'a8', 'h8', 'e2', 'e4', 'd5', 'g1', 'b7']
    
    passed = 0
    for square in test_squares:
        try:
            coord = square_to_coord(square)
            result = coord_to_square(coord)
            if result == square:
                print(f"✓ {square} -> {coord} -> {result}")
                passed += 1
            else:
                print(f"✗ {square} -> {coord} -> {result} (Expected: {square})")
        except Exception as e:
            print(f"✗ {square} -> Error: {e}")
    
    print(f"Passed {passed}/{len(test_squares)} round trip tests\n")

def test_move_validation():
    print("Testing move validation:")
    
    from app import app
    with app.app_context():
        from app import current_position
        
        if current_position is None:
            print("❌ current_position is None, initializing game first")
            return
        
        # Try to generate valid moves
        try:
            valid_moves = list(current_position.gen_moves())
            print(f"Found {len(valid_moves)} valid moves")
            
            # Convert the first 5 moves to algebraic notation for easier reading
            algebraic_moves = [(coord_to_square(m[0]), coord_to_square(m[1])) for m in valid_moves[:5]]
            print(f"Sample moves: {algebraic_moves}")
            
            # Check if e2-e4 is a valid move
            e2 = square_to_coord('e2')
            e4 = square_to_coord('e4')
            move = (e2, e4)
            
            if move in valid_moves:
                print(f"✓ e2-e4 ({e2}-{e4}) is a valid move")
            else:
                print(f"❌ e2-e4 ({e2}-{e4}) is NOT a valid move")
                print(f"Valid moves from e2: {[(e2, to) for (fr, to) in valid_moves if fr == e2]}")
        except Exception as e:
            print(f"❌ Error generating moves: {e}")

if __name__ == "__main__":
    print("Testing coordinate conversion functions")
    print("======================================\n")
    
    # Run tests
    test_square_to_coord()
    test_coord_to_square()
    test_round_trip()
    
    # Test move validation (requires app initialization)
    try:
        test_move_validation()
    except Exception as e:
        print(f"❌ Error in move validation: {e}")
    
    print("\nTests completed.") 