#!/bin/bash

# Script to run app.py in background and make it survive terminal close
sudo apt-get update
sudo apt-get -y upgrade
sudo apt install -y python3-pip
sudo apt install -y libgl1

pip install -r requirements.txt
pip install -r UI/requirements.txt

PYTHON_SCRIPT="app.py"

# Run using nohup so it won't stop if terminal is killed
nohup python3 "$PYTHON_SCRIPT" > output.log 2>&1 &

echo "Started $PYTHON_SCRIPT in background. Logs: output.log"