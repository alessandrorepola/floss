#!/usr/bin/env bash
set -Eeuo pipefail

# Setup script for the FastAPI project (bug 11) using Python 3.8.x

# Ensure we run from the script directory (stabilizes relative paths)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$SCRIPT_DIR"

VENV_NAME="fastapi-bug6"
REQUIRED_PY="3.8"

# Select a Python 3.8 interpreter
PY=""
for cmd in python3.8 python3 python; do
  if command -v "$cmd" >/dev/null 2>&1; then
    PY="$cmd"
    break
  fi
done
if [[ -z "$PY" ]]; then
  echo "Python 3.8 not found. Please install Python 3.8 and try again." >&2
  exit 1
fi

# Verify Python is 3.8.x
if ! "$PY" - <<'PYCODE'
import sys
sys.exit(0 if sys.version_info[:2] == (3,8) else 1)
PYCODE
then
  echo "Python 3.8.x is required (found $("$PY" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'))." >&2
  exit 1
fi

# Create venv
"$PY" -m venv "$VENV_NAME"

# Activate venv
if [[ -f "$VENV_NAME/bin/activate" ]]; then
  source "$VENV_NAME/bin/activate"
else
  echo "Virtualenv activation script not found." >&2
  exit 1
fi

$PY -m pip install -q --upgrade pip setuptools wheel

# Install PyFault
$PY -m pip install -q -e ../../../

# Clone or update BugsInPy
if [[ -d BugsInPy/.git ]]; then
  git -C BugsInPy pull --ff-only
else
  git clone https://github.com/soarsmu/BugsInPy.git
fi

# Add BugsInPy tools to PATH for this shell
BUGSINPY_BIN="$(pwd)/BugsInPy/framework/bin"
case ":$PATH:" in
  *":$BUGSINPY_BIN:"*) ;;
  *) export PATH="$PATH:$BUGSINPY_BIN" ;;
esac

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 6 -w "./"

# Install FastAPI deps and package
REQ_FILE="fastapi/bugsinpy_requirements.txt"
if [[ ! -f "$REQ_FILE" ]]; then
  echo "Requirements file not found: $REQ_FILE" >&2
  exit 1
fi
$PY -m pip install -q -r "$REQ_FILE"
$PY -m pip install -q -e fastapi

# Copy pyfault.conf if present
if [[ -f "pyfault.conf" ]]; then
  cp -f "pyfault.conf" "fastapi/"
else
  echo "Warning: pyfault.conf not found, skipping copy." >&2
fi

echo "Setup completed."