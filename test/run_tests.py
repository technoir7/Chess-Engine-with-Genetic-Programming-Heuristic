#!/usr/bin/env python3
"""
Test runner script for the Genetic Chess Engine.
This script runs both Python and JavaScript tests.
"""
import os
import sys
import unittest
import webbrowser
from threading import Timer

# Get the absolute path to the JS test file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JS_TEST_PATH = os.path.join(BASE_DIR, 'static', 'js', 'tests', 'test.html')

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test.test_complete_initial_board import CompleteInitialBoardTest

def run_python_tests():
    """Run the Python unit tests for the backend."""
    print("Running Python backend tests...\n")
    
    # Load tests from the test_chess_app module
    try:
        from test_chess_app import ChessAppTestCase
        
        # Create a test suite and run it
        test_suite = unittest.TestLoader().loadTestsFromTestCase(ChessAppTestCase)
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        
        # Return True if all tests passed
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing test module: {e}")
        return False

def open_js_tests():
    """Open the JavaScript tests in a web browser."""
    print("\nRunning JavaScript frontend tests...\n")
    
    # Convert the file path to a file URL
    if os.path.exists(JS_TEST_PATH):
        file_url = f"file://{JS_TEST_PATH}"
        print(f"Opening browser to: {file_url}\n")
        webbrowser.open(file_url)
    else:
        print(f"Error: JavaScript test file not found at: {JS_TEST_PATH}")

if __name__ == "__main__":
    print("=" * 80)
    print("Running Genetic Chess Engine Tests")
    print("=" * 80)
    
    # Run Python tests first
    python_success = run_python_tests()
    
    # Run JavaScript tests after 1 second
    Timer(1.0, open_js_tests).start()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add our test classes
    test_suite.addTest(unittest.makeSuite(CompleteInitialBoardTest))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return appropriate exit code for CI/CD systems
    if not python_success:
        print("\nSome Python tests failed!")
        sys.exit(1)
    else:
        print("\nAll Python tests passed!")
        # We don't know the result of JS tests since they run in the browser
        sys.exit(not result.wasSuccessful()) 