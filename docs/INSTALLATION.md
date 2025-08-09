# PyFault Installation Guide

This guide provides comprehensive installation instructions for PyFault across different platforms and use cases.

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Memory**: 512 MB RAM (2GB+ recommended for large projects)
- **Disk Space**: 100 MB for installation + space for coverage data

### Recommended Requirements
- **Python**: 3.10 or 3.11 (for best performance)
- **Memory**: 4 GB RAM or more
- **CPU**: Multi-core processor (for faster test execution)

## 🚀 Quick Installation

### Option 1: Basic Installation
```bash
pip install pyfault
```

### Option 2: With UI Components
```bash
pip install pyfault[ui]
```

### Option 3: Full Installation (UI + Development tools)
```bash
pip install pyfault[ui,dev]
```

## 📦 Installation Methods

### 1. PyPI Installation (Recommended)

#### Standard Installation
```bash
# Install core PyFault functionality
pip install pyfault

# Verify installation
pyfault --help
```

#### With Optional Dependencies
```bash
# Install with UI components (Streamlit dashboard)
pip install pyfault[ui]

# Install with development dependencies
pip install pyfault[dev]

# Install everything
pip install pyfault[ui,dev]
```

### 2. Development Installation

For contributors or users who want the latest features:

```bash
# Clone the repository
git clone https://github.com/example/pyfault.git
cd pyfault

# Install in development mode
pip install -e .

# Or with optional dependencies
pip install -e ".[ui,dev]"
```

### 3. Virtual Environment Installation

#### Using venv (Python 3.3+)
```bash
# Create virtual environment
python -m venv pyfault-env

# Activate virtual environment
# On Windows:
pyfault-env\Scripts\activate
# On macOS/Linux:
source pyfault-env/bin/activate

# Install PyFault
pip install pyfault[ui]
```

#### Using conda
```bash
# Create conda environment
conda create -n pyfault python=3.10
conda activate pyfault

# Install PyFault
pip install pyfault[ui]
```

#### Using pipenv
```bash
# Create Pipfile and install
pipenv install pyfault[ui]

# Activate environment
pipenv shell
```

### 4. Docker Installation

#### Using Pre-built Image (Coming Soon)
```bash
# Pull the official image
docker pull pyfault/pyfault:latest

# Run PyFault in container
docker run -v $(pwd):/workspace pyfault/pyfault:latest run --source-dir /workspace/src
```

#### Building Custom Image
```dockerfile
# Dockerfile
FROM python:3.10-slim

# Install PyFault
RUN pip install pyfault[ui]

# Set working directory
WORKDIR /workspace

# Default command
CMD ["pyfault", "--help"]
```

```bash
# Build and run
docker build -t my-pyfault .
docker run -v $(pwd):/workspace my-pyfault run --source-dir src
```

## 🔧 Platform-Specific Instructions

### Windows

#### Using Windows Package Manager (winget)
```powershell
# Install Python if not already installed
winget install Python.Python.3.10

# Install PyFault
pip install pyfault[ui]
```

#### Using Chocolatey
```powershell
# Install Python
choco install python

# Install PyFault
pip install pyfault[ui]
```

#### PowerShell Execution Policy
If you encounter execution policy issues:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS

#### Using Homebrew
```bash
# Install Python
brew install python@3.10

# Install PyFault
pip3 install pyfault[ui]
```

#### Using pyenv
```bash
# Install pyenv
brew install pyenv

# Install and use Python 3.10
pyenv install 3.10.8
pyenv global 3.10.8

# Install PyFault
pip install pyfault[ui]
```

### Linux

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.10 python3.10-pip python3.10-venv

# Install PyFault
python3.10 -m pip install pyfault[ui]
```

#### CentOS/RHEL/Fedora
```bash
# Install Python
sudo dnf install python3.10 python3.10-pip

# Install PyFault
python3.10 -m pip install pyfault[ui]
```

#### Arch Linux
```bash
# Install Python
sudo pacman -S python python-pip

# Install PyFault
pip install pyfault[ui]
```

## 🧪 Verification

### Test Installation
```bash
# Check PyFault version
pyfault --version

# Display help to verify all commands are available
pyfault --help

# Test individual commands
pyfault test --help
pyfault fl --help
pyfault run --help
pyfault ui --help
```

### Test with Sample Project
```bash
# Create a simple test project
mkdir pyfault-test
cd pyfault-test

# Create a simple Python file
cat > calculator.py << 'EOF'
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        return 0  # Bug: should raise exception
    return a / b
EOF

# Create a test file
cat > test_calculator.py << 'EOF'
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    # This test will fail due to the bug
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)
EOF

# Run PyFault
pyfault run

# Check if report.json was created
ls -la report.json
```

## 🔧 Dependency Management

### Core Dependencies
PyFault automatically installs these core dependencies:
- `rich>=14.0.1` - Enhanced terminal output
- `click>=8.1.8` - Command-line interface framework
- `pytest>=8.3.5` - Test execution framework
- `numpy>=1.24.4` - Numerical computations
- `coverage>=7.6.1` - Code coverage measurement
- `pytest-cov>=4.0.0` - Pytest coverage integration

### UI Dependencies (Optional)
Install with `pip install pyfault[ui]`:
- `streamlit>=1.45.0` - Web dashboard framework
- `plotly>=5.22.0` - Interactive visualizations
- `pandas>=2.0.3` - Data manipulation and analysis

### Development Dependencies (Optional)
Install with `pip install pyfault[dev]`:
- `mypy` - Static type checking
- `black` - Code formatting
- `flake8` - Code linting
- `pre-commit` - Git hooks for code quality

### Resolving Dependency Conflicts

#### Common Issues

**Conflicting Package Versions:**
```bash
# Use pip to check for conflicts
pip check

# Upgrade conflicting packages
pip install --upgrade package-name
```

**Python Version Incompatibility:**
```bash
# Check Python version
python --version

# Ensure you're using Python 3.9+
```

**Missing System Dependencies:**
```bash
# On Ubuntu/Debian - install build tools if needed
sudo apt install build-essential python3-dev

# On CentOS/RHEL - install development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel
```

## 🐛 Troubleshooting

### Installation Issues

#### Permission Errors
```bash
# Use user installation
pip install --user pyfault[ui]

# Or create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pyfault[ui]
```

#### Network/Proxy Issues
```bash
# Configure proxy for pip
pip install --proxy http://proxy.company.com:8080 pyfault[ui]

# Or use alternative index
pip install -i https://pypi.org/simple/ pyfault[ui]
```

#### SSL Certificate Issues
```bash
# Upgrade certificates
pip install --upgrade certifi

# Or temporarily disable SSL verification (not recommended for production)
pip install --trusted-host pypi.org --trusted-host pypi.python.org pyfault[ui]
```

### Runtime Issues

#### Command Not Found
```bash
# Ensure pip installation directory is in PATH
python -m site --user-base

# Add to PATH if needed (Linux/macOS)
export PATH="$PATH:$(python -m site --user-base)/bin"

# Or use python -m
python -m pyfault --help
```

#### Import Errors
```bash
# Check installation
pip show pyfault

# Reinstall if corrupted
pip uninstall pyfault
pip install pyfault[ui]
```

### Performance Issues

#### Slow Installation
```bash
# Use faster mirrors
pip install -i https://pypi.douban.com/simple/ pyfault[ui]

# Or install without dependencies first
pip install --no-deps pyfault
pip install -r requirements.txt
```

#### Memory Issues During Installation
```bash
# Use no-cache option
pip install --no-cache-dir pyfault[ui]

# Or install dependencies separately
pip install streamlit plotly pandas
pip install pyfault
```

## 🔄 Upgrading PyFault

### Check Current Version
```bash
pyfault --version
pip show pyfault
```

### Upgrade to Latest Version
```bash
# Upgrade PyFault
pip install --upgrade pyfault[ui]

# Or force reinstall
pip install --force-reinstall pyfault[ui]
```

### Upgrade from Development Version
```bash
# Pull latest changes
cd pyfault
git pull origin main

# Reinstall
pip install -e ".[ui,dev]"
```

## 🗑️ Uninstallation

### Remove PyFault
```bash
# Uninstall PyFault and its dependencies
pip uninstall pyfault

# Remove configuration files (optional)
rm -rf ~/.pyfault

# Remove virtual environment (if used)
rm -rf pyfault-env
```

### Clean Uninstall
```bash
# List all installed packages
pip freeze > installed_packages.txt

# Remove PyFault
pip uninstall pyfault

# Check for orphaned dependencies
pip-autoremove pyfault -y  # If you have pip-autoremove installed
```

## 🆘 Getting Help

### Installation Support

If you encounter issues during installation:

1. **Check the FAQ** in this guide
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Installation command used

### Community Resources

- **GitHub Issues**: https://github.com/example/pyfault/issues
- **Documentation**: https://pyfault.readthedocs.io
- **Examples**: See the `examples/` directory in the repository

---

This installation guide should help you get PyFault running on your system. For usage instructions, see the User Guide documentation.
