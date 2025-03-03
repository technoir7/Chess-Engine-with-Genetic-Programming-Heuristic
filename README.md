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
# Or if using Python 3 explicitly:
pip3 install -r requirements.txt
```

## Quick Start

The easiest way to get started is to use the start script, which provides a menu-driven interface:

```bash
# Make the script executable first (if needed)
chmod +x start.py

# Then run it
./start.py
# Or with explicit Python 3:
python3 start.py
```

Alternatively, you can use our recommended run script which handles environment issues:

```bash
# Make the script executable 
chmod +x run.sh

# Run the application directly
./run.sh
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
# Or with explicit Python 3:
python3 help.py
```

2. Start the Flask server (choose one of the following methods):
```bash
# Method 1: Using the run.sh script (recommended)
./run.sh

# Method 2: Using the run script (opens browser automatically)
./run.py
# Or with explicit Python 3:
python3 run.py

# Method 3: Using Flask directly
python3 app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

**Note on connectivity:** The server is configured to listen on all interfaces (0.0.0.0). If you can't connect to localhost, please check:
- No firewall is blocking port 5000
- No other service is using port 5000
- Try accessing the app directly at http://127.0.0.1:5000
- Run the troubleshooting tool: `./troubleshoot.py`

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
# Or with explicit Python 3:
python3 run_tests.py
```

To run only the Python backend tests:
```bash
python3 test_chess_app.py
```

To run only the JavaScript frontend tests, open the following file in your browser:
```
static/js/tests/test.html
```

## Troubleshooting

If you encounter any issues running the application, use the troubleshooting tool:

```bash
./troubleshoot.py
# Or with explicit Python 3:
python3 troubleshoot.py
```

This tool will:
- Check your Python version
- Verify Flask is installed correctly
- Check if port 5000 is available
- Test the Flask application
- Provide detailed suggestions for fixing common issues

For detailed troubleshooting information, see the TROUBLESHOOTING.md file.

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
├── troubleshoot.py          # Troubleshooting tool
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
