#!/bin/bash

# Activate virtual environment
source /app/venv/bin/activate  # Adjust path if necessary

# Start aria2c with RPC
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon \
  --max-tries=50 --retry-wait=3 --continue=true --min-split-size=4M --split=10 --allow-overwrite=true

# Wait for aria2c RPC server to be ready
echo "Waiting for aria2c to start..."
for i in {1..10}; do
  if curl -s http://localhost:6800/jsonrpc > /dev/null; then
    echo "aria2c is up!"
    break
  else
    echo "Still waiting for aria2c..."
    sleep 1
  fi
done

# Start the Python bot
python3 terabox.py
