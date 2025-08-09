# Contributing to PyFault

Thank you for your interest in contributing to PyFault! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

There are many ways to contribute to PyFault:

- **Report bugs** and request features
- **Improve documentation** and examples
- **Submit code** fixes and enhancements
- **Add new SBFL formulas** and algorithms
- **Enhance visualizations** and dashboard features
- **Write tests** and improve code coverage
- **Optimize performance** for large codebases

## 🚀 Getting Started

### Development Environment Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pyfault.git
   cd pyfault
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev,ui]"
   ```

4. **Verify installation**:
   ```bash
   python -m pytest tests/ -v
   mypy src
   ```

### Development Dependencies

The development environment includes:

- **Testing**: `pytest`, `pytest-cov`
- **Type Checking**: `mypy`
- **Code Formatting**: `black`
- **Linting**: `flake8`
- **Pre-commit Hooks**: `pre-commit`

### Pre-commit Hooks

Set up pre-commit hooks to automatically format and check code:

```bash
pre-commit install
```

This will run the following checks before each commit:
- Code formatting with Black
- Import sorting with isort
- Type checking with mypy
- Linting with flake8
- Basic file checks

## 📋 Development Workflow

### 1. Issue-Based Development

- Browse existing issues or create a new one
- Discuss the approach before starting work on significant changes
- Reference the issue in your pull request

### 2. Branch Naming

Use descriptive branch names:
- `feature/add-new-formula`
- `bugfix/fix-coverage-calculation`
- `docs/improve-user-guide`
- `refactor/reorganize-cli-module`

### 3. Commit Messages

Follow conventional commit format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Examples:
```
feat(formulas): add DStar3 formula implementation
fix(cli): handle missing configuration file gracefully
docs(api): update FL engine documentation
test(formulas): add comprehensive Ochiai formula tests
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `style`: Code style changes

### 4. Pull Request Process

1. **Create a focused PR**: Address one issue or feature per PR
2. **Update documentation**: Include relevant documentation updates
3. **Add tests**: Ensure new code has appropriate test coverage
4. **Update changelog**: Add entry to CHANGELOG.md if applicable
5. **Request review**: Tag relevant maintainers for review

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_cli.py              # CLI interface tests
├── test_fl.py               # Fault localization engine tests
├── test_formulas.py         # SBFL formula tests
├── test_ui_cli.py          # UI command tests
├── test_e2e.py             # End-to-end integration tests
├── test_performance.py     # Performance benchmarks
└── fixtures/               # Test data and fixtures
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_formulas.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run performance tests
python -m pytest tests/test_performance.py -v
```

### Writing Tests

#### Unit Tests
```python
import pytest
from pyfault.formulas import OchiaiFormula

class TestOchiaiFormula:
    def test_basic_calculation(self):
        formula = OchiaiFormula()
        result = formula.calculate(n_cf=5, n_nf=3, n_cp=2, n_np=10)
        expected = 5 / (math.sqrt(8 * 7))
        assert abs(result - expected) < 1e-6
    
    def test_zero_failed_covering(self):
        formula = OchiaiFormula()
        result = formula.calculate(n_cf=0, n_nf=8, n_cp=5, n_np=10)
        assert result == 0.0
```

#### Integration Tests
```python
def test_complete_fl_pipeline(tmp_path):
    # Setup test project structure
    source_dir = tmp_path / "src"
    test_dir = tmp_path / "tests"
    # ... create test files ...
    
    # Run complete pipeline
    config = TestConfig(source_dir=str(source_dir))
    runner = TestRunner(config)
    result = runner.run_tests()
    
    # Verify results
    assert len(result.failed_tests) > 0
    assert result.coverage_data is not None
```

#### UI Tests
```python
def test_dashboard_overview_tab():
    # Mock data for testing
    test_data = {
        "totals": {"test_statistics": {"total_tests": 10}},
        "files": {"test.py": {"suspiciousness": {"ochiai": {"1": 0.5}}}}
    }
    
    # Test dashboard components
    with patch('streamlit.metric') as mock_metric:
        show_overview(test_data, "ochiai")
        mock_metric.assert_called()
```

### Test Data and Fixtures

Create reusable test fixtures:

```python
@pytest.fixture
def sample_coverage_data():
    return {
        "meta": {"version": "7.6.1", "timestamp": "2025-01-01T00:00:00"},
        "files": {
            "src/module.py": {
                "executed_lines": [1, 2, 5],
                "summary": {"covered_lines": 3, "num_statements": 10},
                "contexts": {"test_a": [1, 2], "test_b": [5]}
            }
        },
        "totals": {"covered_lines": 3, "num_statements": 10}
    }

@pytest.fixture
def sample_fl_report():
    return {
        "meta": {"timestamp": "2025-01-01T00:00:00"},
        "totals": {"sbfl_formulas": ["ochiai"]},
        "files": {
            "src/module.py": {
                "suspiciousness": {"ochiai": {"1": 0.8, "2": 0.6, "5": 0.3}}
            }
        }
    }
```

## 🧮 Adding New SBFL Formulas

### Formula Implementation

1. **Create the formula class**:
   ```python
   # src/pyfault/formulas/my_formula.py
   from .base import SBFLFormula
   
   class MyNewFormula(SBFLFormula):
       """
       Implementation of My New Formula.
       
       Formula: Custom calculation based on coverage statistics
       
       Reference: Author, A. (Year). Paper Title. Conference/Journal.
       """
       
       def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
           if n_cf == 0:
               return 0.0
           
           # Your formula implementation here
           numerator = n_cf * (n_cf + n_np)
           denominator = (n_cf + n_nf) * (n_cf + n_cp)
           
           return safe_divide(numerator, denominator)
   ```

2. **Add to the formula registry**:
   ```python
   # src/pyfault/formulas/__init__.py
   from .my_formula import MyNewFormula
   
   FORMULA_REGISTRY = {
       # ... existing formulas ...
       "mynew": MyNewFormula,
   }
   ```

3. **Write comprehensive tests**:
   ```python
   # tests/test_formulas.py
   class TestMyNewFormula:
       def test_basic_calculation(self):
           formula = MyNewFormula()
           result = formula.calculate(4, 2, 3, 5)
           # Test against expected value
           
       def test_edge_cases(self):
           formula = MyNewFormula()
           
           # Test zero cases
           assert formula.calculate(0, 5, 3, 2) == 0.0
           
           # Test single values
           assert formula.calculate(1, 0, 0, 0) == 1.0
           
       def test_symmetry_properties(self):
           # Test mathematical properties if applicable
           pass
   ```

4. **Add documentation**:
   ```python
   class MyNewFormula(SBFLFormula):
       """
       Implementation of My New Formula for fault localization.
       
       This formula provides enhanced fault localization by considering
       the relationship between failed test coverage and passing test
       coverage in a unique way.
       
       Formula: (n_cf * (n_cf + n_np)) / ((n_cf + n_nf) * (n_cf + n_cp))
       
       Where:
           n_cf: Number of failed tests covering the line
           n_nf: Number of failed tests not covering the line  
           n_cp: Number of passed tests covering the line
           n_np: Number of passed tests not covering the line
       
       Reference:
           Author, A., et al. (2025). "Advanced SBFL Techniques"
           International Conference on Software Engineering.
       
       Use Cases:
           - Projects with high test coverage
           - Scenarios with many passing tests
           - When traditional formulas show low discrimination
       """
   ```

### Formula Evaluation

Include evaluation criteria for new formulas:

1. **Effectiveness**: How well does it identify real faults?
2. **Discrimination**: Can it distinguish between faulty and non-faulty lines?
3. **Stability**: Does it perform consistently across different projects?
4. **Computational efficiency**: How fast is the calculation?

## 🎨 UI and Visualization Contributions

### Adding Dashboard Features

1. **Create new visualization function**:
   ```python
   # src/pyfault/ui/dashboard.py
   def show_my_new_visualization(data: Dict[str, Any], formula: str):
       """Show custom visualization for fault localization data."""
       st.subheader("My New Visualization")
       
       # Extract data
       files_data = data.get('files', {})
       
       # Create visualization
       fig = px.scatter(...)  # Your Plotly visualization
       st.plotly_chart(fig, use_container_width=True)
   ```

2. **Add to dashboard tabs**:
   ```python
   # In main() function
   tab1, tab2, tab3, tab_new = st.tabs([
       "Overview", "Source Code", "Analysis", "My New Tab"
   ])
   
   with tab_new:
       show_my_new_visualization(data, selected_formula)
   ```

3. **Test the visualization**:
   ```python
   def test_my_new_visualization():
       test_data = {...}  # Mock data
       
       with patch('streamlit.plotly_chart') as mock_chart:
           show_my_new_visualization(test_data, "ochiai")
           mock_chart.assert_called_once()
   ```

### Dashboard Best Practices

- **Performance**: Use caching for expensive computations
- **Responsiveness**: Design for different screen sizes
- **Accessibility**: Include helpful tooltips and descriptions
- **Interactivity**: Allow users to customize views
- **Export**: Provide data export capabilities where useful

## 📚 Documentation Contributions

### Documentation Structure

```
docs/
├── README.md               # Main project overview
├── USER_GUIDE.md          # Comprehensive user guide
├── API_REFERENCE.md       # API documentation
├── ARCHITECTURE.md        # System architecture
├── CONTRIBUTING.md        # This file
├── CHANGELOG.md          # Release notes
└── examples/             # Usage examples
```

### Writing Guidelines

1. **Clear and Concise**: Use simple, direct language
2. **Examples**: Include practical code examples
3. **Structure**: Use consistent headings and formatting
4. **Completeness**: Cover all major use cases
5. **Accuracy**: Keep documentation synchronized with code

### API Documentation

Use consistent docstring format:

```python
def calculate_suspiciousness(self, input_file: str, output_file: str) -> None:
    """
    Calculate suspiciousness scores and generate report.
    
    This method processes coverage data from test execution and applies
    configured SBFL formulas to calculate suspiciousness scores for each
    line of code.
    
    Args:
        input_file: Path to input coverage data file (JSON format)
        output_file: Path for output fault localization report
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        JSONDecodeError: If input file contains invalid JSON
        ValueError: If coverage data format is invalid
        
    Example:
        >>> config = FLConfig(formulas=["ochiai", "tarantula"])
        >>> engine = FLEngine(config)
        >>> engine.calculate_suspiciousness("coverage.json", "report.json")
    """
```

## 🔧 Code Style and Standards

### Python Style Guidelines

We follow PEP 8 with some specific conventions:

#### Formatting
- **Line Length**: 88 characters (Black default)
- **Imports**: Use isort for import organization
- **Strings**: Prefer double quotes for strings
- **Type Hints**: Required for all public APIs

#### Naming Conventions
```python
# Classes: PascalCase
class SBFLFormula:
    pass

# Functions and variables: snake_case
def calculate_suspiciousness():
    pass

test_result = None

# Constants: UPPER_SNAKE_CASE
DEFAULT_CONFIG_FILE = "pyfault.conf"

# Private members: _leading_underscore
def _internal_helper():
    pass
```

#### Code Organization
```python
"""Module docstring."""

# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import click
import numpy as np

# Local imports
from .config import TestConfig
from .runner import TestRunner
```

### Type Hints

Use comprehensive type hints:

```python
from typing import Dict, List, Optional, Union, Any

def process_coverage_data(
    coverage: Dict[str, Any],
    formulas: List[str],
    threshold: Optional[float] = None
) -> Dict[str, Dict[int, float]]:
    """Process coverage data with type hints."""
    pass
```

### Error Handling

Use specific exception types and informative messages:

```python
class PyFaultError(Exception):
    """Base exception for PyFault errors."""
    pass

class ConfigurationError(PyFaultError):
    """Raised when configuration is invalid."""
    pass

def load_config(config_file: str) -> Dict[str, Any]:
    try:
        with open(config_file) as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(
            f"Configuration file not found: {config_file}"
        )
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid JSON in config file {config_file}: {e}"
        )
```

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Try latest version** to ensure bug still exists
3. **Isolate the problem** with minimal reproduction case

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command: `pyfault run --source-dir src`
2. With configuration: [attach pyfault.conf]
3. See error: [error message]

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g., Ubuntu 20.04, Windows 10, macOS 12]
- Python version: [e.g., 3.9.7]
- PyFault version: [e.g., 0.1.0]

**Additional context**
- Project structure
- Test framework used
- Any relevant log output (use `--verbose`)
```

## 🌟 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.

**Use case**
Describe how this feature would be used in practice.
```

## 📋 Release Process

### Version Numbering

We use semantic versioning (SemVer):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Checklist

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update changelog** with release notes
3. **Run full test suite** and ensure all tests pass
4. **Update documentation** if needed
5. **Create release tag** and GitHub release
6. **Publish to PyPI** (maintainers only)

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be respectful** and considerate in all interactions
- **Be collaborative** and help others learn and contribute
- **Be patient** with newcomers and different skill levels
- **Focus on the code** and technical merit, not personal attributes

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code contributions and reviews

### Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- GitHub contributor statistics

## 📞 Getting Help

If you need help with contributing:

1. **Check the documentation** (especially this guide and the user guide)
2. **Search existing issues** and discussions
3. **Create a new issue** with the "question" label
4. **Join GitHub Discussions** for community support

We appreciate all contributions, from small bug fixes to major features. Thank you for helping make PyFault better!
