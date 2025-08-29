# PyFault Examples

This directory contains real-world examples demonstrating PyFault's fault localization capabilities on actual software projects with known bugs.

## Available Examples

### FastAPI Examples
Real bugs from the FastAPI web framework, sourced from the [BugsInPy](https://github.com/soarsmu/BugsInPy) dataset.

**Features:**
- **Centralized Setup**: Single parametrized script for all bugs (`./setup.sh <bug_number>`)
- **Shared Configuration**: Common `pyfault.conf` for consistent analysis
- **Isolated Environments**: Separate virtual environments per bug

**Available Bugs:**
- **[bug2](fastapi/bug2/)**: FastAPI Bug #2 - OpenAPI schema generation issue
- **[bug3](fastapi/bug3/)**: FastAPI Bug #3 - Request validation problem  
- **[bug6](fastapi/bug6/)**: FastAPI Bug #6 - Dependency injection error
- **[bug11](fastapi/bug11/)**: FastAPI Bug #11 - Response model validation issue

**Quick Start:**
```bash
cd examples/fastapi
./setup.sh 11  # Setup bug 11
cd fastapi && pyfault run
```

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
./setup.sh <bug_number>  # e.g., ./setup.sh 11
cd fastapi && pyfault run
```

### Other Examples
Each has its own setup script:
```bash
cd examples/<example-name>
./setup.sh
# Follow example-specific instructions
```

## Example Structure

- **FastAPI**: Centralized setup with shared configuration
- **PyGraphistry**: Individual setup with project-specific configuration  
- **Dummy**: Simple setup for testing purposes

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
