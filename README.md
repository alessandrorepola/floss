# PyFault

**A Python framework for Spectrum-Based Fault Localization (SBFL)**

PyFault is a comprehensive tool for automated fault localization using Spectrum-Based Fault Localization (SBFL) techniques. It helps developers identify potential bug locations in their Python code by analyzing test execution traces and applying statistical formulas to calculate suspiciousness scores for code lines.

## 🚀 Features

- **Multiple SBFL Formulas**: Supports popular formulas including Ochiai, Tarantula, Jaccard, and D*
- **Interactive Dashboard**: Web-based visualization with treemaps, source code highlighting, and coverage matrices
- **Comprehensive CLI**: Complete command-line interface for all fault localization tasks
- **Test Integration**: Seamless integration with pytest for test execution and coverage collection
- **Configurable**: Flexible configuration via configuration files and command-line options
- **Performance Analysis**: Compare different SBFL formulas and analyze their effectiveness

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/example/pyfault.git
cd pyfault

# Install in development mode
pip install -e .

# Install with UI dependencies
pip install -e ".[ui]"

# Install with development dependencies
pip install -e ".[dev]"
```

### Package Dependencies

- **Core**: `rich`, `click`, `pytest`, `numpy`, `coverage`
- **UI (optional)**: `streamlit`, `plotly`, `pandas`
- **Development (optional)**: `mypy`, `black`, `flake8`, `pre-commit`

## 🎯 Quick Start

### 1. Basic Usage

Run the complete fault localization pipeline on your project:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Run fault localization (will auto-detect tests)
pyfault run --source-dir src --output report.json

# Launch interactive dashboard
pyfault ui --report report.json
```

### 2. Step-by-Step Usage

```bash
# Step 1: Run tests with coverage collection
pyfault test --source-dir src --output coverage.json

# Step 2: Calculate fault localization scores
pyfault fl --input coverage.json --output report.json --formulas ochiai,tarantula

# Step 3: Visualize results
pyfault ui --report report.json
```

### 3. Configuration File

Create a `pyfault.conf` file in your project root:

```ini
[test]
source_dir = src
output_file = coverage.json
ignore = */__init__.py,*/migrations/*
omit = */__init__.py,*/tests/*

[fl]
input_file = coverage.json
output_file = report.json
formulas = ochiai, tarantula, jaccard, dstar2
```

## 🔧 CLI Commands

### `pyfault test` - Test Execution with Coverage

Runs tests using pytest with enhanced coverage collection.

```bash
pyfault test [OPTIONS]

Options:
  -s, --source-dir TEXT    Source code directory to analyze (default: .)
  -t, --test-dir TEXT      Test directory (auto-detected by pytest)
  -o, --output TEXT        Output file for coverage data (default: coverage.json)
  -k, --test-filter TEXT   Filter tests using pytest -k pattern
  --ignore TEXT            File patterns to ignore (multiple allowed)
  --omit TEXT              File patterns to omit from coverage (multiple allowed)
  -c, --config TEXT        Configuration file (default: pyfault.conf)
  -v, --verbose            Enable verbose output
```

### `pyfault fl` - Fault Localization

Calculates suspiciousness scores using SBFL formulas.

```bash
pyfault fl [OPTIONS]

Options:
  -i, --input TEXT         Input coverage file (default: coverage.json)
  -o, --output TEXT        Output report file (default: report.json)
  -f, --formulas TEXT      SBFL formulas to use (multiple allowed)
  -c, --config TEXT        Configuration file (default: pyfault.conf)
  -v, --verbose            Enable verbose output
```

### `pyfault run` - Complete Pipeline

Executes the complete fault localization pipeline.

```bash
pyfault run [OPTIONS]

Options:
  -s, --source-dir TEXT    Source code directory to analyze (default: .)
  -t, --test-dir TEXT      Test directory (auto-detected by pytest)
  -o, --output TEXT        Output file for FL report (default: report.json)
  -k, --test-filter TEXT   Filter tests using pytest -k pattern
  --ignore TEXT            File patterns to ignore (multiple allowed)
  --omit TEXT              File patterns to omit from coverage (multiple allowed)
  -f, --formulas TEXT      SBFL formulas to use (multiple allowed)
  -c, --config TEXT        Configuration file (default: pyfault.conf)
  -v, --verbose            Enable verbose output
```

### `pyfault ui` - Interactive Dashboard

Launches the web-based visualization dashboard.

```bash
pyfault ui [OPTIONS]

Options:
  -r, --report TEXT        Report file to visualize (default: report.json)
  -p, --port INTEGER       Port for the dashboard (default: 8501)
  --no-open               Do not auto-open browser
  -v, --verbose            Enable verbose output
```

## 📊 Dashboard Features

The PyFault dashboard provides comprehensive visualization and analysis tools:

### Overview Tab
- **Test Execution Summary**: Total, passed, failed, and skipped tests
- **Code Coverage Analysis**: Statement and branch coverage metrics
- **Fault Localization Readiness**: Analysis preparation statistics
- **Most Suspicious Files**: Ranked list of files with highest suspiciousness

### Source Code Tab
- **Interactive Code Viewer**: Syntax-highlighted source code display
- **Suspiciousness Highlighting**: Color-coded lines based on scores
- **Line-by-Line Analysis**: Detailed suspiciousness scores for each line
- **File Navigation**: Easy browsing through project files

### Test-to-Fault Analysis Tab
- **Coverage Matrix**: Visualization of test-to-code line relationships
- **Test Outcome Mapping**: Failed vs. passed test execution patterns
- **Interactive Filtering**: Focus on specific tests or code sections

### Treemap Tab
- **Hierarchical Visualization**: Project structure with suspiciousness data
- **Directory-Level Analysis**: Aggregate scores at folder level
- **Interactive Navigation**: Drill-down capabilities

### Sunburst Tab
- **Circular Hierarchy**: Alternative view of project structure
- **Proportional Representation**: Size based on suspiciousness scores
- **Multi-Level Analysis**: From project root to individual files

### Formula Comparison Tab
- **Side-by-Side Analysis**: Compare different SBFL formulas
- **Statistical Metrics**: Distribution analysis and correlation studies
- **Performance Benchmarking**: Effectiveness comparison

### Formula Performance Tab
- **Effectiveness Metrics**: Precision, recall, and F1-score analysis
- **Ranking Quality**: Top-N analysis and ranking effectiveness
- **Export Capabilities**: Generate performance reports

## 🧪 SBFL Formulas

PyFault implements several proven SBFL formulas:

### Ochiai
- **Formula**: `n_cf / sqrt((n_cf + n_nf) * (n_cf + n_cp))`
- **Description**: One of the most effective SBFL formulas in practice
- **Use Case**: General-purpose fault localization

### Tarantula
- **Formula**: `(n_cf / (n_cf + n_nf)) / ((n_cf / (n_cf + n_nf)) + (n_cp / (n_cp + n_np)))`
- **Description**: First and most well-known SBFL formula
- **Use Case**: Baseline comparison and research

### Jaccard
- **Formula**: `n_cf / (n_cf + n_nf + n_cp)`
- **Description**: Similarity coefficient adapted for fault localization
- **Use Case**: Alternative similarity-based approach

### D* (D-Star)
- **Formula**: `n_cf^star / (n_cp + n_nf)`
- **Description**: Optimized binary formula (star typically 2 or 3)
- **Use Case**: High-performance fault localization

Where:
- `n_cf`: Number of failed tests covering the line
- `n_nf`: Number of failed tests not covering the line
- `n_cp`: Number of passed tests covering the line
- `n_np`: Number of passed tests not covering the line

## 🏗️ Architecture

PyFault is organized into several key modules:

### Core Components

- **`pyfault.test`**: Test execution and coverage collection
- **`pyfault.fl`**: Fault localization engine and algorithms
- **`pyfault.formulas`**: SBFL formula implementations
- **`pyfault.cli`**: Command-line interface
- **`pyfault.ui`**: Interactive dashboard and visualizations

### Data Flow

1. **Test Execution**: Run tests with coverage instrumentation
2. **Coverage Collection**: Generate detailed execution traces
3. **Formula Application**: Calculate suspiciousness scores
4. **Report Generation**: Create structured output with metadata
5. **Visualization**: Interactive analysis and exploration

## 📝 Configuration

### Configuration File Format

PyFault uses INI-style configuration files:

```ini
[test]
source_dir = src
test_dir = tests
output_file = coverage.json
ignore = */__init__.py, */migrations/*, */vendor/*
omit = */__init__.py, */tests/*, */venv/*

[fl]
input_file = coverage.json
output_file = report.json
formulas = ochiai, tarantula, jaccard, dstar2
```

### Configuration Options

#### Test Section
- `source_dir`: Directory containing source code to analyze
- `test_dir`: Directory containing test files (auto-detected if not specified)
- `output_file`: Output file for coverage data
- `ignore`: Patterns to ignore during test discovery
- `omit`: Patterns to omit from coverage analysis

#### FL Section
- `input_file`: Input coverage file from test execution
- `output_file`: Output file for fault localization report
- `formulas`: Comma-separated list of SBFL formulas to apply

## 🔄 Integration

### CI/CD Integration

PyFault can be integrated into continuous integration pipelines:

```yaml
# GitHub Actions example
- name: Run Fault Localization
  run: |
    pip install pyfault[ui]
    pyfault run --source-dir src --output fl_report.json
    
- name: Upload FL Report
  uses: actions/upload-artifact@v3
  with:
    name: fault-localization-report
    path: fl_report.json
```

### IDE Integration

PyFault reports can be imported into various development environments for enhanced debugging workflows.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/example/pyfault.git
cd pyfault
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Type checking
mypy src

# Code formatting
black src tests
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by GZoltar and other fault localization tools
- Built on the foundation of established SBFL research
- Thanks to the Python testing and coverage ecosystem

## 🆘 Support

- **Documentation**: Full documentation available in the `docs/` directory
- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join the community discussions for questions and support

---

**PyFault** - Making fault localization accessible and effective for Python developers.
