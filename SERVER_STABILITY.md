# Server Stability Guide for Genetic Chess Engine

This guide provides information about the server stability tools and how to use them to ensure your Genetic Chess Engine stays running.

## Understanding the Issue

The Genetic Chess Engine Flask application may occasionally stop running due to various reasons including:
- Flask's built-in development server is not designed for production use
- Memory leaks or resource exhaustion
- Unhandled exceptions that crash the application
- Network interruptions

## Server Stability Tools

To address these issues, we've created two key tools:

### 1. Server Keep-Alive Script (`server_keep_alive.sh`)

This script is a robust solution to ensure your server stays running:

- **Continuous Monitoring**: Regularly checks if the server is responding to HTTP requests
- **Automatic Restart**: If the server becomes unresponsive, it restarts it automatically
- **Comprehensive Logging**: Records all events in a log file for troubleshooting
- **Graceful Shutdown**: Properly handles termination signals

#### How to use:

```bash
# Start the server with default settings (port 5001)
./server_keep_alive.sh

# Use a custom port
PORT=5002 ./server_keep_alive.sh

# Run with debug mode enabled
DEBUG=true ./server_keep_alive.sh
```

The script will create a log file (`server_keepalive.log`) that tracks server activity, including starts, stops, and restarts.

### 2. Server Testing Script (`test/test_server_alive.py`)

This script verifies that your server is running correctly and can respond to key API endpoints:

- **Comprehensive Testing**: Tests the main API endpoints (/, /initialize, /move)
- **Response Time Monitoring**: Measures how quickly your server responds
- **Server Auto-Start**: Can start the server using the keep-alive script if it's not running

#### How to use:

```bash
# Run the test script
./test/test_server_alive.py
```

If the tests pass, your server is functioning correctly. If not, check the server logs for details.

## Best Practices for Server Stability

1. **Always use the keep-alive script**: Instead of using `run.sh` directly, use `server_keep_alive.sh` which adds monitoring and auto-restart capabilities.

2. **Monitor the logs**: Check the `server_keepalive.log` periodically to identify patterns of server crashes.

3. **Run the test script regularly**: Use the `test_server_alive.py` script to verify that all endpoints are working correctly.

4. **Consider a production server**: For long-term deployment, consider using a production-grade WSGI server like Gunicorn or uWSGI instead of Flask's development server.

## Troubleshooting

If you continue to experience stability issues:

1. **Check the logs**: Look at both `server_keepalive.log` and `server.log` for errors
2. **Increase restart limit**: Edit `MAX_RESTARTS` in `server_keep_alive.sh` if needed
3. **Adjust check interval**: Change `CHECK_INTERVAL` for more/less frequent monitoring
4. **Memory usage**: If the server crashes frequently, check for memory leaks using tools like `top` or `htop`

## Common Issues and Solutions

| Issue | Possible Solution |
|-------|-------------------|
| Server crashes immediately | Check for syntax errors or dependency issues |
| Server crashes after specific moves | Look for bugs in the move validation or AI logic |
| Server becomes unresponsive over time | Memory leak - consider implementing a scheduled restart |
| Multiple server processes running | Kill all python processes and restart with keep-alive script |

For persistent issues, consider implementing more detailed logging in the Flask application itself. 