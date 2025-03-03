#!/usr/bin/env python3
"""
Script to run piece rendering tests using CPython for faster execution.
"""
import os
import sys
import unittest
import importlib.util
import time

def load_test_module(module_path):
    """Load a test module from a file path."""
    module_name = os.path.basename(module_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_piece_rendering_tests():
    """Run the piece rendering tests."""
    print("=" * 80)
    print("Running Piece Rendering Tests with CPython")
    print("=" * 80)
    
    start_time = time.time()
    
    # Get the absolute path to the test directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test modules to run
    test_modules = [
        os.path.join(base_dir, "test_piece_rendering_issues.py"),
        os.path.join(base_dir, "test_board_rendering_issues.py")
    ]
    
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add tests from each module
    for test_module_path in test_modules:
        if os.path.exists(test_module_path):
            try:
                # Load the module
                test_module = load_test_module(test_module_path)
                
                # Find all test case classes in the module
                for name in dir(test_module):
                    obj = getattr(test_module, name)
                    if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                        # Add tests from this test case class
                        tests = unittest.defaultTestLoader.loadTestsFromTestCase(obj)
                        test_suite.addTests(tests)
                
                print(f"Added tests from {os.path.basename(test_module_path)}")
            except Exception as e:
                print(f"Error loading module {test_module_path}: {e}")
        else:
            print(f"Test module not found: {test_module_path}")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print(f"Test Results: {result.testsRun} tests run in {duration:.2f} seconds")
    print(f"  Passes: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 80)
    
    # Return appropriate exit code for CI/CD systems
    if result.wasSuccessful():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(run_piece_rendering_tests()) 