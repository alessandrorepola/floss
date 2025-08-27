#!/usr/bin/env bash
set -Eeuo pipefail

# Setup script for the FastAPI project (bug 2) using Python 3.8.3

VENV_NAME="fastapi-bug2"
REQUIRED_PY="3.8.3"

# Pick a Python 3.8 interpreter
PY=""
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "Python 3.8 not found. Please install Python 3.8.3 and try again." >&2
  exit 1
fi

# Verify exact Python version 3.8.3
CURRENT_VER="$($PY -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' || true)"
if [[ "$CURRENT_VER" != "$REQUIRED_PY" ]]; then
  echo "Python $REQUIRED_PY is required (found $CURRENT_VER). Please install the exact version and try again." >&2
  exit 1
fi

# Create venv
$PY -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

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
bugsinpy-checkout -p fastapi -v 0 -i 2 -w "./"

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