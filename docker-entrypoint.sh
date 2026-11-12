#!/bin/sh
# Initialise la config persistante au premier démarrage (volume vide).
set -e
if [ ! -f "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "$CONFIG_PATH")"
  cp /app/config.default.yaml "$CONFIG_PATH"
  echo "initialized $CONFIG_PATH from image defaults"
fi
mkdir -p /app/data/recordings /app/data/telemetry
exec "$@"
