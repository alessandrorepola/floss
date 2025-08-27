#!/usr/bin/env bash
set -Eeuo pipefail

# Setup script for the PyGraphistry project

VENV_NAME="pygraphistry"

# Pick a Python interpreter
PY=""
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "Python not found. Please install Python and try again." >&2
  exit 1
fi

# Create venv
$PY -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

$PY -m pip install -q --upgrade pip setuptools wheel

# Install PyFault
$PY -m pip install -q -e ../../

# Clone PyGraphistry
if [[ -d pygraphistry/.git ]]; then
  git -C pygraphistry pull --ff-only
else
  git clone https://github.com/graphistry/pygraphistry.git
fi

# Checkout buggy version identified with BugSwarm
cd pygraphistry
git checkout 856839d7fa6b21bec4924fe8d09b422bc8c7f9b4
$PY -m pip install -e .
$PY -m pip install -e .[test]
cd ..

# Copy pyfault.conf if present
if [[ -f "pyfault.conf" ]]; then
  cp -f "pyfault.conf" "pygraphistry/"
else
  echo "Warning: pyfault.conf not found, skipping copy." >&2
fi

echo "Setup completed."