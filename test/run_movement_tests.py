#!/usr/bin/env python3
import unittest
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our test cases
from test_piece_movement_issues import TestPieceMovementIssues

if __name__ == '__main__':
    print("Running tests to diagnose piece movement issues...")
    
    # Create a test suite with our test cases
    test_suite = unittest.TestSuite()
    
    # Add specific test methods to diagnose the issue
    test_suite.addTest(TestPieceMovementIssues('test_coordinate_transformations'))
    test_suite.addTest(TestPieceMovementIssues('test_move_flow_debug'))
    test_suite.addTest(TestPieceMovementIssues('test_move_function_directly'))
    test_suite.addTest(TestPieceMovementIssues('test_move_handler_request_processing'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(test_suite)
    
    # Report results
    if results.wasSuccessful():
        print("\nAll tests PASSED! The issue may have been resolved.")
    else:
        print("\nSome tests FAILED. Check the output above for details on the issues.")
        
    sys.exit(not results.wasSuccessful()) 