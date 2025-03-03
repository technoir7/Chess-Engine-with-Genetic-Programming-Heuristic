# Persistent Server for Genetic Chess Engine

This document explains how to use the persistent server solution for the Genetic Chess Engine, ensuring the server remains running and responsive.

## Problem

The Flask development server used by the Genetic Chess Engine has limitations:

1. **Stability Issues**: The server may stop responding or terminate unexpectedly
2. **Environmental Conflicts**: Python environment variables can cause startup failures
3. **No Auto-Recovery**: The standard setup doesn't automatically restart the server if it crashes

## Solution

The persistent server solution addresses these issues with:

1. **Process Monitoring**: Continuously checks if the server is running and responsive
2. **Auto-Restart**: Automatically restarts the server if it crashes or becomes unresponsive
3. **Environment Handling**: Properly manages Python environment variables
4. **Production-Grade Server**: Uses Gunicorn WSGI server for better stability (if available)
5. **Comprehensive Logging**: Records all server activity for troubleshooting

## Quick Start

Start the server with the default settings:

```bash
./start_server.sh
```

This will:
1. Clear problematic environment variables
2. Start the server (using Gunicorn if available)
3. Monitor the server and restart it if needed
4. Log all activity to `persistent_server.log`

The server will be available at [http://localhost:5001/](http://localhost:5001/).

## Advanced Options

You can customize the server behavior with command-line options:

```bash
./start_server.sh --port 5002 --host 127.0.0.1 --debug
```

Available options:

- `--port PORT`: Change the port (default: 5001)
- `--host HOST`: Change the host (default: 127.0.0.1)
- `--debug`: Enable debug mode
- `--check-interval SECONDS`: Change how often to check server health (default: 5)
- `--max-restarts COUNT`: Change maximum restart attempts (default: 10)
- `--no-gunicorn`: Don't use Gunicorn even if available

## Monitoring and Logs

Monitor the server status with:

```bash
tail -f persistent_server.log
```

This log file contains:
- Server start/stop events
- Restart attempts
- Health check results
- Server process output

## Stopping the Server

To stop the server gracefully, press `Ctrl+C` in the terminal where it's running.

This will:
1. Terminate the server process
2. Stop all monitoring
3. Log the shutdown

## Troubleshooting

### Server Won't Start

If the server fails to start:

1. Check for port conflicts:
   ```bash
   lsof -i :5001
   ```

2. Review the logs:
   ```bash
   cat persistent_server.log
   ```

3. Try with debug mode:
   ```bash
   ./start_server.sh --debug
   ```

### Environment Issues

If you encounter Python environment issues:

1. Make sure you're using the wrapper script:
   ```bash
   ./start_server.sh
   ```

2. Manually clear environment variables:
   ```bash
   unset PYTHONHOME PYTHONPATH
   source venv/bin/activate
   ./run_persistent_server.py
   ```

## Best Practices

1. **Always use the wrapper script**: The `start_server.sh` script ensures a clean environment.

2. **Monitor the logs**: Check the logs for any issues or patterns of failures.

3. **Use Gunicorn**: Install Gunicorn for better stability:
   ```bash
   source venv/bin/activate
   pip install gunicorn
   ```

4. **Consider a process manager**: For production, consider using a process manager like systemd or Supervisor for more robust monitoring.

## How It Works

The persistent server solution consists of:

1. **Main Script (`run_persistent_server.py`)**: Manages the server process, monitoring, and auto-restart functionality

2. **Wrapper Script (`start_server.sh`)**: Ensures a clean environment before starting the server

3. **Health Checking**: Regularly checks if the server is responding to HTTP requests

4. **Process Management**: Monitors the server process status and restarts it if needed

When started, the server will automatically recover from many types of failures, ensuring continuous availability. 