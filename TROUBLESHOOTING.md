# Troubleshooting the Genetic Chess Engine

## Issue: Unable to Connect to localhost:5000

If you're experiencing issues connecting to the application at localhost:5000, one of the following might be the cause:

### 1. Cursor IDE Environment Variables Issue

We identified that when running Python from within Cursor IDE, it sets some environment variables that conflict with the normal Python environment:

```
PYTHONHOME = '/tmp/.mount_cursorLnAW8I/usr/'
PYTHONPATH = '/tmp/.mount_cursorLnAW8I/usr/share/pyshared/:'
```

These variables cause Python to look for its standard libraries in the wrong locations, resulting in errors like:

```
Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding
ModuleNotFoundError: No module named 'encodings'
```

### Solution:

We've created a wrapper script `run.sh` that:
1. Unsets these problematic environment variables
2. Uses the virtual environment if available
3. Starts the application with a clean Python environment

To run the application:

```bash
# Make the script executable (if not already)
chmod +x run.sh

# Run the application
./run.sh
```

### 2. Python Version Compatibility

The codebase was originally designed for Python 2, but has been updated to be compatible with Python 3. If you're still encountering syntax errors, they might be related to Python 2 vs Python 3 differences.

### 3. Port Already in Use

If port 5000 is already being used by another application, you won't be able to connect. 

To check if the port is in use:
```bash
lsof -i :5000
```

To use a different port:
```bash
export PORT=5001
./run.sh
```

Then connect to `http://localhost:5001`

### 4. Virtual Environment and Dependencies

The application requires Flask and other packages to be installed. We recommend using a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
./run.sh
```

## If Problems Persist

Run the troubleshooting tool:

```bash
python troubleshoot.py
```

This will check for common issues and provide more specific recommendations. 