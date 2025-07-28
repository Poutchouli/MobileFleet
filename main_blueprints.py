# main.py
# Refactored main entry point using Flask Blueprints architecture.

import os
from app import create_app

# Create the Flask application using the factory pattern
app = create_app()

# Import models to ensure they're registered with SQLAlchemy
from app.models import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
