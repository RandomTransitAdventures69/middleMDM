#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SERVER_DIR="$ROOT_DIR/server"
PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python 3 is required. Install Python 3.8 or newer and retry." >&2
    exit 1
fi

echo "Creating an isolated Python environment..."
"$PYTHON" -m venv "$SERVER_DIR/.venv"
VENV_PYTHON="$SERVER_DIR/.venv/bin/python"
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r "$SERVER_DIR/requirements.txt"

ENV_FILE="$SERVER_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    SECRET_KEY=$("$VENV_PYTHON" -c 'import secrets; print(secrets.token_urlsafe(48))')
    ENROLLMENT_SECRET=$("$VENV_PYTHON" -c 'import secrets; print(secrets.token_urlsafe(48))')
    cat > "$ENV_FILE" <<EOF
FLASK_ENV=development
SECRET_KEY=$SECRET_KEY
ENROLLMENT_SECRET=$ENROLLMENT_SECRET
DATABASE_URL=sqlite:///./middlemdm_dev.db
HOST=127.0.0.1
PORT=5001
SESSION_COOKIE_SECURE=false
EOF
    chmod 600 "$ENV_FILE"
fi

echo "Initializing the database and administrator account..."
cd "$SERVER_DIR"
"$VENV_PYTHON" -m flask --app run init-db
echo "Setup complete. Start the server with: $ROOT_DIR/run.sh"
