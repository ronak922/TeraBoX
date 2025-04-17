#!/bin/sh

# Start aria2c in background (not using --daemon)
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all \
  --max-tries=50 --retry-wait=3 --continue=true \
  --min-split-size=4M --split=10 --allow-overwrite=true \
  > /tmp/aria2.log 2>&1 &

# Wait for aria2c to be ready
echo "Waiting for aria2c to start..."
for i in $(seq 1 10); do
  if curl -s http://localhost:6800/jsonrpc > /dev/null; then
    echo "aria2c is up!"
    break
  fi
  echo "Still waiting for aria2c..."
  sleep 1
done

# Debug log (optional)
cat /tmp/aria2.log

# Run your Python bot
python terabox.py
