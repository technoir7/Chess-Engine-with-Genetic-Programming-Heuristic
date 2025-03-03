# Server Stability Solution for Genetic Chess Engine

## Problem Statement

The Genetic Chess Engine server was experiencing stability issues:
1. The server would sometimes stop responding after a period of time
2. The server process would occasionally terminate unexpectedly
3. Environmental issues with Python variables were causing startup failures

This solution addresses these problems by providing tools to ensure server stability, automatic recovery, and proper environment handling.

## Solution Components

1. **Server Monitoring Script** (`test/monitor_server.py`): Continuously checks server health and logs any issues.
2. **Server Keep-Alive** (`run_stable_server.py`): Keeps the server running, automatically restarting it if it crashes.
3. **Server Stability Tests** (`test/test_server_alive.py`): Verifies server functionality with unit tests.
4. **Environment-Aware Wrapper Scripts**:
   - `run_test.sh`: Runs Python scripts with a clean environment.
   - `test_server.sh`: Quickly checks server status and runs tests.

## Verification and Testing

The server stability has been thoroughly tested and verified:

1. **All Tests Passing**: We've confirmed that all server stability tests are now passing, including:
   - Basic server connectivity
   - Initialization endpoint functionality
   - Move processing capabilities
   - Game restart functionality
   - Server response time tests

2. **Verified API Endpoints**:
   - `GET /`: Confirms the server is running
   - `POST /initialize`: Initializes a new game board with specified difficulty
   - `POST /move`: Processes player moves and AI responses

3. **Timeout Handling**: The tests account for potentially longer processing times when the AI is calculating moves.

## Usage Instructions

### Starting the Server

Choose one of the following methods to start the server:

1. **Stable Server (Recommended)**:
   ```bash
   ./run_stable_server.py
   ```
   This will keep the server running, automatically restarting it if it crashes.

2. **Standard Server**:
   ```bash
   ./run.sh
   ```
   This starts the server but won't automatically restart it if it crashes.

### Testing Server Status

To quickly check if the server is running and functioning correctly:

```bash
./test_server.sh
```

This will:
1. Check if the server is running
2. Run basic functionality tests
3. Report any issues found

### Comprehensive Monitoring

For continuous monitoring of the server:

```bash
python test/monitor_server.py
```

Options:
- `--duration <seconds>`: How long to monitor (default: indefinite)
- `--interval <seconds>`: How often to check the server (default: 10 seconds)
- `--log <file>`: Custom log file location (default: server_monitor.log)

## Troubleshooting

### Environment Variable Issues

If you encounter Python environment errors such as `ModuleNotFoundError: No module named 'encodings'`, this is typically caused by problematic environment variables like `PYTHONHOME` or `PYTHONPATH`.

**Solution Options**:

1. **Use Provided Wrapper Scripts**:
   - For testing: `./run_test.sh <script.py>`
   - For server status check: `./test_server.sh`

2. **Manual Environment Cleaning**:
   ```bash
   unset PYTHONHOME PYTHONPATH
   source venv/bin/activate  # If using a virtual environment
   python <script.py>
   ```

### Server Not Responding

If the server doesn't respond, try the following steps:

1. Check if the server process is running:
   ```bash
   ps aux | grep python | grep app.py
   ```

2. Verify there are no port conflicts:
   ```bash
   lsof -i :5001
   ```

3. Restart the server with the stable server script:
   ```bash
   ./run_stable_server.py
   ```

4. Examine the logs for errors:
   ```bash
   cat server_monitor.log  # If monitoring was running
   ```

## Configuration Options

The server and monitoring tools are configurable to accommodate different needs:

### Server Configuration

- **Port**: Default is 5001, modify in `app.py` or `config.py`
- **Difficulty Levels**: Supported in the `/initialize` endpoint (values: 1-5)

### Monitoring Configuration

- **Check Interval**: How often to check server status (default: 10s)
- **Log Location**: Custom location for logging server events
- **Alerting**: Can be configured to send notifications (see monitor_server.py)

## Successful Testing Results

We've confirmed that all tests are now passing with the current implementation. This includes:

1. **Basic Connectivity**: The server responds to basic requests within milliseconds.
2. **Game Initialization**: New games can be successfully created with different difficulty levels.
3. **Move Processing**: The server correctly processes legal chess moves and generates AI responses.
4. **Game Restart**: New games can be started after completing previous games.
5. **Response Times**: All endpoints respond within acceptable time frames.

If you need to verify these results yourself, run the test script:

```bash
./run_test.sh test/test_server_alive.py
```

A successful test run will show all tests passing with OK status.

## Directory Structure

```
genetic_chess_engine/
├── app.py                   # Main Flask application
├── run.sh                   # Original run script (not recommended)
├── run_stable_server.py     # New server launcher with keep-alive
├── run_test.sh              # General wrapper for running Python scripts
├── server_keep_alive.sh     # Server monitoring and restart script
├── server_keepalive.log     # Keep-alive monitor logs
├── server.log               # Flask application logs
├── test_server.sh           # Script for testing server functionality
├── README_SERVER_STABILITY.md  # This documentation
└── test/
    └── test_server_alive.py # Server functionality tests
```

## Common Environment Issues and Solutions

| Issue | Description | Solution |
|-------|-------------|----------|
| PYTHONHOME set incorrectly | Points to editor's Python instead of system/venv | Use `run_test.sh` or manually `unset PYTHONHOME` |
| PYTHONPATH conflicts | Includes paths that conflict with venv packages | Use `run_test.sh` or manually `unset PYTHONPATH` |
| ImportError/ModuleNotFoundError | Can't find modules despite them being installed | Use wrapper scripts that fix environment variables |
| "No module named 'encodings'" | Fatal Python error from environment misconfiguration | Use `test_server.sh` to run the test |

## Recommendations for Long-Term Stability

For a more robust production setup, consider:

1. **Use a production WSGI server** like Gunicorn or uWSGI instead of Flask's development server
2. **Set up a process manager** like Supervisor or systemd for more robust process monitoring
3. **Implement a load balancer** if high availability is required
4. **Add comprehensive logging** to the Flask application to better diagnose issues
5. **Consider containerization** with Docker to isolate the application environment 