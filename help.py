#!/usr/bin/env python
"""
Help script for the Genetic Chess Engine.
Provides information about the application and how to use it.
"""
import os
import sys

def display_help():
    """Display help information about the application."""
    print("""
===============================================================================
                           GENETIC CHESS ENGINE
===============================================================================

A chess engine that uses genetic programming to evolve and improve its play 
strategy, with a beautiful web interface.

AVAILABLE COMMANDS:

  ./run.py           - Start the application and open it in your browser
  python app.py      - Start the application without opening the browser
  ./run_tests.py     - Run all tests (both Python and JavaScript)
  python test_chess_app.py - Run just the Python backend tests

HOW TO PLAY:

  1. Start the application using one of the commands above
  2. Open your browser to http://localhost:5000/ if it doesn't open automatically
  3. Select a difficulty level (Easy, Medium, Hard)
  4. Click "New Game" to start a game
  5. Make moves by clicking on a piece and then clicking on the destination square
  6. The AI will respond with its own moves

EVOLVING THE AI:

  1. Click "Evolve AI" in the game interface
  2. Specify the number of generations (higher = better but slower)
  3. Click "Confirm" and wait for the process to complete
  4. Start a new game to play against the improved AI

ADDITIONAL INFORMATION:

  - The source code is available in the project directory
  - Documentation is available in the README.md file
  - Frontend tests can be run by opening static/js/tests/test.html in a browser

===============================================================================
""")

if __name__ == "__main__":
    display_help()
    sys.exit(0) 