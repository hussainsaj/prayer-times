#!/bin/bash

# Activate the virtual environment
source /home/hussain/Desktop/prayer-times/env/bin/activate

# Change to the prayer-times directory
cd /home/hussain/Desktop/prayer-times

# Run the Python script and log output
python3 app.py >> /home/hussain/Desktop/prayer-times/logs/app.log 2>&1 &