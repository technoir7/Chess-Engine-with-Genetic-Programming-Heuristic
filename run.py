#!/usr/bin/env python
"""
Run script for the Genetic Chess Engine web application.
"""
import os
import webbrowser
from threading import Timer
from app import app

def open_browser():
    """Open a browser tab to the application."""
    webbrowser.open_new('http://localhost:5000/')

if __name__ == '__main__':
    # Open browser after a short delay
    port = int(os.environ.get('PORT', 5000))
    Timer(1.5, open_browser).start()
    
    # Start the Flask application
    print("=" * 80)
    print("Genetic Chess Engine")
    print("=" * 80)
    print("\nStarting web server...")
    print("Open your browser to http://localhost:5000/ if it doesn't open automatically")
    print("\nPress Ctrl+C to quit")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=False) 