#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the Flask application
flask run --host=0.0.0.0 --port=$PORT
