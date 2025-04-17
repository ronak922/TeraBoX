#!/bin/bash

# Activate virtual environment
source /app/venv/bin/activate  # Adjust path if necessary

# Start aria2c with RPC
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon --max-tries=50 --retry-wait=3 --continue=true --min-split-size=4M --split=10 --allow-overwrite=true

# Start the Python bot
python3 terabox.py
