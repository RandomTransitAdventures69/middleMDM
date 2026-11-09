#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SERVER_DIR="$ROOT_DIR/server"
VENV_PYTHON="$SERVER_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "Run ./install.sh first to install the server." >&2
    exit 1
fi

cd "$SERVER_DIR"
exec "$VENV_PYTHON" -m flask --app run run \
    --no-reload --host 127.0.0.1 --port "${PORT:-5001}"
