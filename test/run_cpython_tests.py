#!/usr/bin/env python3
"""
Test runner script to execute tests using CPython for faster execution.
This script can be used instead of the default Python interpreter to speed up test execution.
"""

import os
import sys
import unittest
import argparse
import time

def collect_tests(test_pattern=None):
    """
    Discover and collect all tests in the test directory.
    Optionally filter by a test pattern.
    """
    start_dir = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    
    if test_pattern:
        # Load specific tests matching the pattern
        pattern = f"test_{test_pattern}.py" if not test_pattern.startswith("test_") else f"{test_pattern}.py"
        return loader.discover(start_dir, pattern=pattern)
    else:
        # Load all tests
        return loader.discover(start_dir)

def run_tests(test_pattern=None, verbosity=2):
    """
    Run the tests with the given verbosity level.
    """
    print(f"Running tests with CPython interpreter: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    test_suite = collect_tests(test_pattern)
    
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    end_time = time.time()
    
    elapsed = end_time - start_time
    
    # Print summary
    print("\nTest Summary:")
    print(f"Ran {result.testsRun} tests in {elapsed:.2f} seconds")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

def main():
    """
    Parse command-line arguments and run the tests.
    """
    parser = argparse.ArgumentParser(description="Run tests with CPython for faster execution")
    parser.add_argument("test_pattern", nargs="?", help="Pattern to filter test files (without the 'test_' prefix)")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=2,
                        help="Verbosity level (0=quiet, 1=normal, 2=verbose)")
    
    args = parser.parse_args()
    
    return run_tests(test_pattern=args.test_pattern, verbosity=args.verbosity)

if __name__ == "__main__":
    sys.exit(main()) 