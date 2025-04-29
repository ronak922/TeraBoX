#!/bin/sh

# Default Configurations
ARIA2_RPC_PORT=${ARIA2_RPC_PORT:-6800}  # Default to port 6800 if not set
ARIA2_LOG=${ARIA2_LOG:-/tmp/aria2.log}  # Default log file location
ARIA2_MAX_TRIES=${ARIA2_MAX_TRIES:-50}  # Default max retries
ARIA2_RETRY_WAIT=${ARIA2_RETRY_WAIT:-3} # Default retry wait time in seconds

# Start aria2c in background (not using --daemon)
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all \
  --rpc-listen-port=${ARIA2_RPC_PORT} \
  --max-tries=${ARIA2_MAX_TRIES} --retry-wait=${ARIA2_RETRY_WAIT} --continue=true \
  --min-split-size=4M --split=10 --allow-overwrite=true \
  > ${ARIA2_LOG} 2>&1 &

# Wait for aria2c to be ready
echo "Waiting for aria2c to start on port ${ARIA2_RPC_PORT}..."
for i in $(seq 1 10); do
  if curl -s http://localhost:${ARIA2_RPC_PORT}/jsonrpc > /dev/null; then
    echo "aria2c is up!"
    break
  fi
  echo "Still waiting for aria2c... ($i/10)"
  sleep 1
done

# If aria2c isn't up after retries, exit with an error
if ! curl -s http://localhost:${ARIA2_RPC_PORT}/jsonrpc > /dev/null; then
  echo "Error: aria2c did not start within the expected time. Check logs for more details."
  exit 1
fi

# Optional: log aria2 output
echo "aria2c logs:"
cat ${ARIA2_LOG}

# Launch the Python bot
echo "Starting the bot..."
exec python terabox.py
