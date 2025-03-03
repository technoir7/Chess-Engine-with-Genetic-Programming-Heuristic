#!/usr/bin/env python3
"""
Run script for the Genetic Chess Engine application.
This script starts the Flask server and opens the application in a web browser.
"""

import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open the browser to the application URL."""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Get host from environment variable or use default
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Construct URL (use localhost for browser, even if server binds to 0.0.0.0)
    url = f'http://localhost:{port}'
    webbrowser.open(url)
    print(f"Opening browser to {url}")

if __name__ == "__main__":
    print("Starting Genetic Chess Engine...")
    
    # Schedule browser opening
    Timer(1.5, open_browser).start()
    
    # Import Flask app and run it
    try:
        from app import app
        
        # Get configuration from environment variables
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'False').lower() in ('true', 't', '1')
        
        # Start the Flask app
        print(f"Server will be available at http://localhost:{port}/")
        app.run(debug=debug, host=host, port=port)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0) 