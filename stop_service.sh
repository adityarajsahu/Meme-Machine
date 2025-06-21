#!/bin/bash

# Script to kill process using port 8080
rm output.log

PORT=8080

PID=$(lsof -t -i:$PORT)

if [ -z "$PID" ]; then
  echo "No process found using port $PORT"
else
  echo "Killing process $PID using port $PORT"
  kill -9 $PID
fi