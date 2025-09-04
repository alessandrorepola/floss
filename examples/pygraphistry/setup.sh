#!/usr/bin/env bash
set -Eeuo pipefail
PS4='+ [${BASH_SOURCE##*/}:${LINENO}] '
set -x
trap 'status=$?; echo "ERROR: command failed: ${BASH_COMMAND} (exit ${status}) at ${BASH_SOURCE[0]}:${LINENO}" >&2; exit ${status}' ERR

# Setup script for the PyGraphistry project

# Ensure we run from the script directory (stabilizes relative paths)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$SCRIPT_DIR"
echo "==> Working directory: $SCRIPT_DIR"

VENV_NAME="venv"

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
echo "==> Using Python interpreter: $PY ($($PY --version 2>&1))"

# Create venv
$PY -m venv "$VENV_NAME"
echo "==> Activating virtual environment"
source "$VENV_NAME/bin/activate"

$PY -m pip install --upgrade pip setuptools wheel

# Install FLOSS
echo "==> Installing FLOSS (editable) from repository root"
$PY -m pip install -e ../../

# Clone PyGraphistry
echo "==> Ensuring PyGraphistry repository is present"
if [[ -d pygraphistry/.git ]]; then
  git -C pygraphistry pull --ff-only
else
  git clone https://github.com/graphistry/pygraphistry.git
fi

# Checkout buggy version identified with BugSwarm
cd pygraphistry
echo "==> Checking out buggy commit 856839d7"
git checkout 856839d7fa6b21bec4924fe8d09b422bc8c7f9b4
echo "==> Installing PyGraphistry and test extras"
$PY -m pip install -e .
$PY -m pip install -e .[test]
cd ..

# Copy FLOSS.conf if present
if [[ -f "FLOSS.conf" ]]; then
  echo "==> Copying FLOSS.conf into pygraphistry/"
  cp -f "FLOSS.conf" "pygraphistry/"
else
  echo "Warning: FLOSS.conf not found, skipping copy." >&2
fi

echo "Setup completed."
