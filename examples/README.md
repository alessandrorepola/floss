# PyFault Examples

This directory contains real-world examples demonstrating PyFault's fault localization capabilities on actual software projects with known bugs.

## Available Examples

### Cookiecutter Examples
Real bugs from the Cookiecutter project templating tool.

**Features:**
- **Template Generation Issues**: Common problems in project templating
- **File Encoding Problems**: Character encoding and file handling bugs
- **Configuration Validation**: Template configuration validation errors

**Available Bugs:**
- **[bug1](cookiecutter/bug1/)**: Cookiecutter Bug #1 - File encoding issue in context parsing
- **[bug2](cookiecutter/bug2/)**: Cookiecutter Bug #2 - Template variable substitution error

### FastAPI Examples
Real bugs from the FastAPI web framework, sourced from the [BugsInPy](https://github.com/soarsmu/BugsInPy) dataset.

**Features:**
- **Centralized Setup**: Single parametrized script for all bugs (`./setup.sh <bug_number>`)
- **Shared Configuration**: Common `pyfault.conf` for consistent analysis
- **Isolated Environments**: Separate virtual environments per bug

**Available Bugs:**
- **[bug1](fastapi/bug1/)**: FastAPI Bug #1 - Response model handling issue
- **[bug2](fastapi/bug2/)**: FastAPI Bug #2 - OpenAPI schema generation issue
- **[bug3](fastapi/bug3/)**: FastAPI Bug #3 - Request validation problem
- **[bug4](fastapi/bug4/)**: FastAPI Bug #4 - Request body validation error
- **[bug5](fastapi/bug5/)**: FastAPI Bug #5 - Path parameter handling issue
- **[bug6](fastapi/bug6/)**: FastAPI Bug #6 - Dependency injection error
- **[bug7](fastapi/bug7/)**: FastAPI Bug #7 - Response serialization problem
- **[bug8](fastapi/bug8/)**: FastAPI Bug #8 - Authentication middleware issue
- **[bug9](fastapi/bug9/)**: FastAPI Bug #9 - Query parameter validation error
- **[bug10](fastapi/bug10/)**: FastAPI Bug #10 - File upload handling issue
- **[bug11](fastapi/bug11/)**: FastAPI Bug #11 - Response model validation issue
- **[bug12](fastapi/bug12/)**: FastAPI Bug #12 - WebSocket connection error
- **[bug13](fastapi/bug13/)**: FastAPI Bug #13 - Middleware execution order issue
- **[bug14](fastapi/bug14/)**: FastAPI Bug #14 - Exception handling problem
- **[bug15](fastapi/bug15/)**: FastAPI Bug #15 - Static file serving issue
- **[bug16](fastapi/bug16/)**: FastAPI Bug #16 - Background task execution error
- **[multi-bugs](fastapi/multi-bugs/)**: Multiple bugs combined for advanced testing

**Quick Start:**
```bash
cd examples/fastapi
./setup.sh 11  # Setup bug 11
cd fastapi && pyfault run
```

**Bug Patches:**
Each bug directory includes a `bug_patch.txt` file containing the exact patch that fixes the bug. This allows you to:
- Understand the root cause of each bug
- Compare PyFault's fault localization results with the actual fix
- Apply the fix manually to test the repair

### PyGraphistry Example
Real-world data visualization library example.

- **[pygraphistry](pygraphistry/)**: PyGraphistry project fault localization

### Dummy Example
Simple synthetic example for testing and demonstration purposes.

- **[dummy-example](dummy-example/)**: Basic example with artificial bugs

## Quick Start

Each example includes setup automation and pre-configured PyFault settings:

### FastAPI Examples
```bash
cd examples/fastapi
./setup.sh <bug_number>  # e.g., ./setup.sh 11 (available: 1-16, multi-bugs)
cd fastapi && pyfault run
```

### Cookiecutter Examples
```bash
cd examples/cookiecutter
./setup.sh <bug_number>  # e.g., ./setup.sh 1 (available: 1-2)
# Follow setup-specific instructions
```

### Other Examples
Each has its own setup script:
```bash
cd examples/<example-name>
./setup.sh
# Follow example-specific instructions
```

## Example Structure

- **FastAPI**: Centralized setup with shared configuration (16 bugs + multi-bug scenarios)
- **Cookiecutter**: Individual setup with project-specific configuration (2 bugs)
- **PyGraphistry**: Individual setup with project-specific configuration
- **Dummy**: Simple setup for testing purposes

All examples now include patch files (`bug_patch.txt`) showing the exact fix for each bug.

### Running an Example

1. **Navigate to the example directory:**
   ```bash
   # For FastAPI (centralized)
   cd examples/fastapi

   # For others (individual)
   cd examples/pygraphistry
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

3. **Execute PyFault:**
   ```bash
   # If setup completed successfully, the project will be in a subdirectory
   cd fastapi  # or pygraphistry for the PyGraphistry example
   pyfault run
   ```

4. **View results:**
   ```bash
   pyfault ui --report report.json
   ```

## Requirements

- **Python 3.8.3+** (FastAPI examples require exactly Python 3.8.3)
- **Git** (for cloning example projects)
- **Unix-like environment** (Linux, macOS, or WSL on Windows)
- **Internet connection** (for downloading example projects)

## Example Structure

Each example follows this structure:
```
example_name/
├── setup.sh           # Automated setup script
├── pyfault.conf       # PyFault configuration
├── report.json        # Pre-generated results (optional)
├── bug_patch.txt      # Patch file showing the actual bug fix
└── README.md          # Example-specific documentation
```

After running `setup.sh`, the directory will also contain:
```
example_name/
├── project_name/      # Downloaded project with bug
├── venv_name/         # Python virtual environment
└── BugsInPy/         # BugsInPy framework (for FastAPI examples)
```

## Troubleshooting

### Python Version Issues
FastAPI examples require exactly Python 3.8.3. If you encounter version errors:
```bash
# Install Python 3.8.3 using pyenv (recommended)
pyenv install 3.8.3
pyenv local 3.8.3

# Or use conda
conda create -n python38 python=3.8.3
conda activate python38
```

### Permission Issues
If setup scripts fail with permission errors:
```bash
chmod +x setup.sh
./setup.sh
```

### Network Issues
If git clone operations fail, ensure you have internet access and try:
```bash
git config --global http.postBuffer 1048576000
```

## Contributing Examples

To add a new example:

1. Create a new directory under the appropriate category
2. Include `setup.sh`, `pyfault.conf`, and `README.md`
3. Test the setup script on a clean environment
4. Document the specific bug and expected results
5. Update this main README.md file

See individual example directories for more detailed information about each bug and its characteristics.
