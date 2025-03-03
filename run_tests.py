#!/usr/bin/env python
"""
Test runner for the Genetic Chess Engine.
Runs all Python tests and opens the browser for JavaScript tests.
"""
import unittest
import os
import sys
import webbrowser
from threading import Timer
import test_chess_app

def run_python_tests():
    """Run all Python unit tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_chess_app)
    
    # Run the tests
    print("=" * 80)
    print("Running Python tests...")
    print("=" * 80)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def open_js_tests():
    """Open the JavaScript tests in a browser."""
    js_test_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static', 'js', 'tests', 'test.html'
    )
    
    test_url = f'file://{js_test_path}'
    print("\n" + "=" * 80)
    print("Opening JavaScript tests in browser...")
    print(f"If the browser doesn't open automatically, go to: {test_url}")
    print("=" * 80)
    
    # Open in browser
    webbrowser.open_new(test_url)

if __name__ == '__main__':
    print("\nGenetic Chess Engine Test Runner")
    print("=" * 80)
    
    # Run Python tests
    python_tests_passed = run_python_tests()
    
    # Open JavaScript tests in browser after a short delay
    Timer(1.5, open_js_tests).start()
    
    # Exit with appropriate status code
    if not python_tests_passed:
        print("\nPython tests failed!")
        sys.exit(1)
    else:
        print("\nPython tests passed. Check browser for JavaScript test results.")
        sys.exit(0) 