#!/usr/bin/env bash
set -Eeuo pipefail
# Show each command before it runs, with file:line context
PS4='+ [${BASH_SOURCE##*/}:${LINENO}] '
set -x
# Helpful error message on failures
trap 'status=$?; echo "ERROR: command failed: ${BASH_COMMAND} (exit ${status}) at ${BASH_SOURCE[0]}:${LINENO}" >&2; exit ${status}' ERR

# Setup script for the FastAPI project (bug 2) using Python 3.8.x

# Ensure we run from the script directory (stabilizes relative paths)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$SCRIPT_DIR"
echo "==> Working directory: $SCRIPT_DIR"

VENV_NAME="fastapi-bug2"
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

# Install PyFault
echo "==> Installing PyFault (editable) from repository root"
$PY -m pip install -e ../../../

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

# Checkout FastAPI buggy version
echo "==> Checking out FastAPI buggy version (issue 2)"
bugsinpy-checkout -p fastapi -v 0 -i 2 -w "$SCRIPT_DIR"

# Install FastAPI deps and package
REQ_FILE="fastapi/bugsinpy_requirements.txt"
if [[ ! -f "$REQ_FILE" ]]; then
  echo "Requirements file not found: $REQ_FILE" >&2
  exit 1
fi
echo "==> Installing FastAPI dependencies from $REQ_FILE"
$PY -m pip install -r "$REQ_FILE"
echo "==> Installing FastAPI in editable mode"
$PY -m pip install -e fastapi

# Copy pyfault.conf if present
if [[ -f "pyfault.conf" ]]; then
  echo "==> Copying pyfault.conf into fastapi/"
  cp -f "pyfault.conf" "fastapi/"
else
  echo "Warning: pyfault.conf not found, skipping copy." >&2
fi

echo "Setup completed."