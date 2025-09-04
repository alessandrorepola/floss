#!/usr/bin/env bash
set -Eeuo pipefail
# PS4='+ [${BASH_SOURCE##*/}:${LINENO}] '
# set -x
trap 'status=$?; echo "ERROR: command failed: ${BASH_COMMAND} (exit ${status}) at ${BASH_SOURCE[0]}:${LINENO}" >&2; exit ${status}' ERR

# Setup script for the FastAPI project using Python 3.8.x
# Usage: ./setup.sh <bug_number>
# Example: ./setup.sh 1

# Check if bug number is provided
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <bug_number>" >&2
  echo "Example: $0 1" >&2
  echo "Available bugs: 1 and 2" >&2
  exit 1
fi

BUG_NUMBER="$1"

# Validate bug number
case "$BUG_NUMBER" in
  1|2)
    echo "==> Setting up Cookiecutter bug $BUG_NUMBER"
    ;;
  *)
    echo "Error: Invalid bug number '$BUG_NUMBER'. Available bugs: 1 to 4" >&2
    exit 1
    ;;
esac

# Ensure we run from the script directory (stabilizes relative paths)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$SCRIPT_DIR"
echo "==> Working directory: $SCRIPT_DIR"

VENV_NAME="cc-bug${BUG_NUMBER}"
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
echo "==> Using Python interpreter: $PY ($($PY --version 2>&1))"

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
echo "==> Creating virtual environment: $VENV_NAME"
"$PY" -m venv "$VENV_NAME"

# Activate venv
if [[ -f "$VENV_NAME/bin/activate" ]]; then
  echo "==> Activating virtual environment"
  source "$VENV_NAME/bin/activate"
else
  echo "Virtualenv activation script not found." >&2
  exit 1
fi

echo "==> Upgrading pip, setuptools, wheel"
$PY -m pip install --upgrade pip setuptools wheel

# Install FLOSS
echo "==> Installing FLOSS (editable) from repository root"
$PY -m pip install -e ../../

# Clone or update BugsInPy
echo "==> Ensuring BugsInPy repository is present"
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
echo "==> Added BugsInPy tools to PATH: $BUGSINPY_BIN"

# Checkout Cookiecutter buggy version
echo "==> Checking out Cookiecutter buggy version (issue $BUG_NUMBER)"
bugsinpy-checkout -p cookiecutter -v 0 -i "$BUG_NUMBER" -w "$SCRIPT_DIR"

# Install Cookiecutter deps and package
echo "==> Installing Cookiecutter in editable mode"
$PY -m pip install -e cookiecutter
$PY -m pip install -r cookiecutter/test_requirements.txt

# Copy FLOSS.conf if present
if [[ -f "FLOSS.conf" ]]; then
  echo "==> Copying FLOSS.conf into cookiecutter/"
  cp -f "FLOSS.conf" "cookiecutter/"
else
  echo "Warning: FLOSS.conf not found, skipping copy." >&2
fi

echo "Setup completed for Cookiecutter bug $BUG_NUMBER."
echo "Virtual environment: $VENV_NAME"
echo "To activate the environment manually: source $VENV_NAME/bin/activate"
