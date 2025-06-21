#!/bin/bash

# Script to run app.py in background and make it survive terminal close

PYTHON_SCRIPT="streamlit_ui.py"

# Run using nohup so it won't stop if terminal is killed
nohup streamlit run "$PYTHON_SCRIPT" > output_ui.log 2>&1 &

echo "Started $PYTHON_SCRIPT in background. Logs: output.log"