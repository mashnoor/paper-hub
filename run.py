#!/usr/bin/env python3
"""
Run the PaperHub Flask application
"""
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    print("Starting PaperHub...")
    print("Access the application at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    app.run(host='0.0.0.0', port=5000) 