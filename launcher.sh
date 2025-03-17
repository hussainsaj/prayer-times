#!/bin/bash

# if virtual environment does not exist, create one
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py >> logs/app.log 2>&1 &