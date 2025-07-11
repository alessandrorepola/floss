<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# PyFault Project Instructions

This is a Python framework for Spectrum-Based Fault Localization (SBFL) inspired by GZoltar.

## Project Structure
- Follow the modular architecture pattern similar to GZoltar
- Implement clean separation between coverage collection, SBFL algorithms, and reporting
- Use type hints throughout the codebase
- Follow PEP 8 style guidelines

## Key Components
- **Coverage Collection**: Use Python's `coverage.py` library with custom hooks
- **SBFL Formulas**: Implement mathematical formulas for suspiciousness calculation
- **Test Integration**: Support pytest and unittest frameworks
- **CLI Interface**: Use Click for command-line interface
- **Report Generation**: Generate HTML/CSV reports with rankings

## Code Quality
- All public functions should have docstrings with examples
- Use dataclasses for structured data
- Implement proper error handling and logging
- Write comprehensive unit tests

## Dependencies
- Prefer well-established libraries (coverage.py, pytest, pandas, numpy)
- Keep dependencies minimal and well-justified
- Use type annotations compatible with Python 3.8+
