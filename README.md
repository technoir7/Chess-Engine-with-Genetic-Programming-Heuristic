# Genetic Chess Engine

A chess engine that uses genetic programming to evolve and improve its play strategy, with a beautiful web interface.

## Features

- Play chess against an AI that evolves using genetic algorithms
- Beautiful, responsive web interface
- Customizable difficulty levels
- Ability to evolve the AI in real-time

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/genetic_chess_engine.git
cd genetic_chess_engine
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

The easiest way to get started is to use the start script, which provides a menu-driven interface:

```bash
./start.py
```

This gives you options to:
1. Start the application
2. Run all tests
3. View help information
4. Exit

## Usage

Alternatively, you can use the following individual commands:

1. For help and getting started information:
```bash
./help.py
```

2. Start the Flask server (choose one of the following methods):
```bash
# Method 1: Using the run script (opens browser automatically)
./run.py

# Method 2: Using Flask directly
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

4. Play chess against the AI:
   - Choose a difficulty level (Easy, Medium, Hard)
   - Click "New Game" to start a game
   - Make moves by clicking and dragging pieces
   - The AI will respond with its own moves

5. Evolve the AI:
   - Click "Evolve AI" to make the AI learn and improve
   - Specify the number of generations for evolution
   - Wait for the process to complete (this may take some time)
   - Start a new game to play against the improved AI

## How It Works

The chess engine uses a genetic programming approach to evolve its evaluation function. The AI uses the minimax algorithm with alpha-beta pruning for searching moves, while the genetic programming component evolves the heuristic used to evaluate board positions.

## Testing

To run all tests (both Python and JavaScript):
```bash
./run_tests.py
```

To run only the Python backend tests:
```bash
python test_chess_app.py
```

To run only the JavaScript frontend tests, open the following file in your browser:
```
static/js/tests/test.html
```

## Project Structure

```
genetic_chess_engine/
├── app.py                   # Flask application
├── chess_logic_by_thomasahle.py # Core chess logic
├── genetic_programming.py   # Genetic algorithm implementation
├── help.py                  # Help information
├── minimax.py               # Minimax search algorithm
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── run.py                   # Script to run the application
├── run_tests.py             # Script to run all tests
├── start.py                 # Menu-driven script to start everything
├── test_chess_app.py        # Backend tests
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css       # CSS styles
│   ├── js/
│   │   ├── chessboard.js    # Chessboard UI
│   │   ├── game.js          # Game logic
│   │   └── tests/           # Frontend tests
│   └── images/
│       └── pieces/          # Chess piece SVGs
└── templates/
    └── index.html           # Main HTML template
```

## License

MIT License
