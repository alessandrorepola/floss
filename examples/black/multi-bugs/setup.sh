#!/usr/bin/env bash
set -Eeuo pipefail
# PS4='+ [${BASH_SOURCE##*/}:${LINENO}] '
# set -x
trap 'status=$?; echo "ERROR: command failed: ${BASH_COMMAND} (exit ${status}) at ${BASH_SOURCE[0]}:${LINENO}" >&2; exit ${status}' ERR

# Setup script for the black project using Python 3.8.x

# Ensure we run from the script directory (stabilizes relative paths)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$SCRIPT_DIR"
echo "==> Working directory: $SCRIPT_DIR"

VENV_NAME="black-bugs"
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
$PY -m pip install -e ../../../

# Ensure BugsInPy's embedded Python can see venv packages (pytest/starlette)
# This exports the venv site-packages into PYTHONPATH so any separate interpreter
# spawned by BugsInPy will resolve the same dependencies.
VENV_SITE=$($PY -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
if [[ -n "${VENV_SITE:-}" && -d "$VENV_SITE" ]]; then
  export PYTHONPATH="$VENV_SITE${PYTHONPATH:+:$PYTHONPATH}"
  echo "==> Exported PYTHONPATH with venv site-packages: $VENV_SITE"
else
  echo "Warning: could not detect venv site-packages; PYTHONPATH not updated." >&2
fi

# Clone or update BugsInPy
echo "==> Cloning BugsInPy-mf repository"
if [[ -d bugsinpy-mf/.git ]]; then
  git -C bugsinpy-mf pull --ff-only
else
  git clone https://github.com/DCallaz/bugsinpy-mf.git
fi

sudo apt-get update
while read -r line; do
  sudo $line -y
done < bugsinpy-mf/dependencies.txt

# Add BugsInPy tools to PATH for this shell
BUGSINPY_BIN="$(pwd)/bugsinpy-mf/framework/bin"
case ":$PATH:" in
  *":$BUGSINPY_BIN:"*) ;;
  *) export PATH="$PATH:$BUGSINPY_BIN" ;;
esac
echo "==> Added BugsInPy-mf tools to PATH: $BUGSINPY_BIN"

# Checkout black buggy version
echo "==> Checking out black buggy version"
bugsinpy-multi-checkout -p black -i 23 -w "$SCRIPT_DIR"

# Install black deps and package
# echo "==> Installing black in editable mode"
$PY -m pip install -e black
$PY -m pip install -e black[test]

# Copy FLOSS.conf if present
if [[ -f "../FLOSS.conf" ]]; then
  echo "==> Copying FLOSS.conf into black/"
  cp -f "../FLOSS.conf" "black/"
else
  echo "Warning: FLOSS.conf not found, skipping copy." >&2
fi

echo "Setup completed for Black bugs."
echo "Virtual environment: $VENV_NAME"
echo "To activate the environment manually: source $VENV_NAME/bin/activate"
