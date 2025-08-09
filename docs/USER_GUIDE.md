# PyFault User Guide

This comprehensive guide will help you get started with PyFault and make the most of its fault localization capabilities.

## 🎯 Getting Started

### Prerequisites

Before using PyFault, ensure you have:

- Python 3.9 or higher
- A Python project with existing tests
- pytest installed (PyFault integrates with pytest)

### Installation

#### Option 1: Basic Installation
```bash
pip install pyfault
```

#### Option 2: With UI Components
```bash
pip install pyfault[ui]
```

#### Option 3: Development Installation
```bash
git clone https://github.com/example/pyfault.git
cd pyfault
pip install -e ".[dev]"
```

### Quick Start

1. **Navigate to your project directory**:
   ```bash
   cd /path/to/your/python/project
   ```

2. **Run fault localization**:
   ```bash
   pyfault run --source-dir src
   ```

3. **View results**:
   ```bash
   pyfault ui
   ```

That's it! PyFault will analyze your code, run your tests, and provide an interactive dashboard to explore potential fault locations.

## 🔧 Configuration

### Configuration File

Create a `pyfault.conf` file in your project root for persistent settings:

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

### Configuration Options Explained

#### Test Section (`[test]`)

- **`source_dir`**: Directory containing your source code to analyze
  - Example: `src`, `myproject`, `.` (current directory)

- **`test_dir`**: Directory containing your test files
  - If not specified, pytest will auto-discover tests
  - Example: `tests`, `test`, `src/tests`

- **`output_file`**: Where to save coverage data
  - Default: `coverage.json`
  - Used as input for fault localization

- **`ignore`**: Patterns to ignore during test discovery
  - Useful for excluding non-test files that match test patterns
  - Example: `*/__init__.py, */migrations/*`

- **`omit`**: Patterns to exclude from coverage analysis
  - Files to exclude from fault localization analysis
  - Example: `*/tests/*, */venv/*, */__pycache__/*`

#### FL Section (`[fl]`)

- **`input_file`**: Coverage data file from test execution
  - Should match `output_file` from test section
  - Default: `coverage.json`

- **`output_file`**: Where to save fault localization results
  - Default: `report.json`
  - Used by the dashboard for visualization

- **`formulas`**: SBFL formulas to calculate
  - Available: `ochiai`, `tarantula`, `jaccard`, `dstar2`, `dstar3`
  - Recommended: `ochiai, tarantula, jaccard, dstar2`

## 📋 Command Reference

### Complete Pipeline: `pyfault run`

The `run` command executes the complete fault localization pipeline in one step.

```bash
pyfault run [OPTIONS]
```

**Common Usage Examples:**

```bash
# Basic usage
pyfault run

# Specify source directory
pyfault run --source-dir src

# Filter tests and specify formulas
pyfault run --test-filter "test_critical" --formulas ochiai,tarantula

# Custom output location
pyfault run --output my_report.json

# Verbose output for debugging
pyfault run --verbose
```

**All Options:**
- `-s, --source-dir TEXT`: Source code directory (default: current directory)
- `-t, --test-dir TEXT`: Test directory (auto-detected if not specified)
- `-o, --output TEXT`: Output report file (default: report.json)
- `-k, --test-filter TEXT`: pytest -k pattern for filtering tests
- `--ignore TEXT`: File patterns to ignore (can be used multiple times)
- `--omit TEXT`: File patterns to omit from coverage (can be used multiple times)
- `-f, --formulas TEXT`: SBFL formulas to use (can be used multiple times)
- `-c, --config TEXT`: Configuration file (default: pyfault.conf)
- `-v, --verbose`: Enable verbose output

### Test Execution: `pyfault test`

Execute tests with enhanced coverage collection.

```bash
pyfault test [OPTIONS]
```

**Usage Examples:**

```bash
# Basic test execution
pyfault test --source-dir src

# Run specific tests
pyfault test --test-filter "test_authentication"

# Custom coverage output
pyfault test --output my_coverage.json

# Exclude additional patterns
pyfault test --omit "*/migrations/*" --omit "*/vendor/*"
```

### Fault Localization: `pyfault fl`

Calculate suspiciousness scores from coverage data.

```bash
pyfault fl [OPTIONS]
```

**Usage Examples:**

```bash
# Basic fault localization
pyfault fl --input coverage.json

# Use specific formulas
pyfault fl --formulas ochiai --formulas tarantula

# Custom input/output files
pyfault fl --input my_coverage.json --output my_report.json
```

### Dashboard: `pyfault ui`

Launch the interactive visualization dashboard.

```bash
pyfault ui [OPTIONS]
```

**Usage Examples:**

```bash
# Launch with default report
pyfault ui

# Specify custom report file
pyfault ui --report my_report.json

# Use custom port
pyfault ui --port 8080

# Don't auto-open browser
pyfault ui --no-open
```

## 🎨 Dashboard Guide

### Overview Tab

The Overview tab provides a high-level summary of your fault localization analysis:

#### Test Execution Summary
- **Total Tests**: Number of tests in your test suite
- **Passed/Failed/Skipped**: Breakdown of test outcomes
- **Quality Indicators**: Assessment of test failure patterns for FL effectiveness

#### Code Coverage Analysis
- **Statement Coverage**: Percentage of code lines executed by tests
- **Branch Coverage**: Percentage of conditional branches covered
- **File-by-File Details**: Coverage breakdown for each source file

#### Fault Localization Analysis
- **Files Analyzed**: Number of source files included in analysis
- **Lines with FL Scores**: Code lines with calculated suspiciousness
- **Available Formulas**: SBFL formulas applied to your code

#### Most Suspicious Files
- **Ranking Table**: Files ordered by maximum suspiciousness score
- **Threshold Control**: Adjust what's considered "suspicious"
- **Quick Navigation**: Click to jump to source code view

#### Recommendations
- **Actionable Insights**: Suggestions for improving FL effectiveness
- **Priority Guidance**: Which files to investigate first
- **Quality Improvements**: How to enhance your testing setup

### Source Code Tab

Interactive source code viewer with fault localization insights:

#### Features
- **File Browser**: Navigate through your project structure
- **Syntax Highlighting**: Color-coded source code display
- **Suspiciousness Overlay**: Lines colored by suspiciousness scores
- **Score Details**: Hover to see exact suspiciousness values
- **Multi-Formula View**: Compare scores across different formulas

#### Usage Tips
- Use the file selector to browse different source files
- Look for red/orange highlighted lines (high suspiciousness)
- Compare how different formulas rank the same lines
- Focus on lines that consistently score high across formulas

### Test-to-Fault Analysis Tab

Detailed analysis of test-to-code relationships:

#### Coverage Matrix
- **Visual Heatmap**: Shows which tests cover which code lines
- **Test Outcomes**: Color-coded by test results (passed/failed)
- **Interactive Filtering**: Focus on specific tests or code sections
- **Pattern Recognition**: Identify common failure patterns

#### Usage Strategies
- Look for code lines covered primarily by failing tests
- Identify tests that cover many suspicious lines
- Find uncovered code that might need additional testing

### Treemap Tab

Hierarchical visualization of your project structure:

#### Features
- **Directory Structure**: Visual representation of your codebase
- **Proportional Sizing**: Area represents suspiciousness levels
- **Color Coding**: Intensity indicates maximum suspiciousness
- **Interactive Navigation**: Click to drill down into directories
- **Threshold Control**: Adjust minimum suspiciousness to display

#### Interpretation
- Large, dark rectangles indicate highly suspicious areas
- Use to get a "bird's eye view" of where problems might be
- Great for identifying problematic modules or packages

### Sunburst Tab

Circular hierarchy visualization:

#### Features
- **Radial Layout**: Circular representation of project structure
- **Nested Rings**: Each ring represents a directory level
- **Angular Size**: Proportional to suspiciousness scores
- **Interactive Exploration**: Click to focus on specific areas

#### Best Use Cases
- Alternative view for complex project hierarchies
- Good for projects with deep directory structures
- Useful for presentations and high-level overviews

### Formula Comparison Tab

Side-by-side analysis of different SBFL formulas:

#### Features
- **Correlation Analysis**: How similarly do formulas rank lines?
- **Distribution Comparison**: Score distribution for each formula
- **Overlap Analysis**: Lines ranked highly by multiple formulas
- **Statistical Metrics**: Quantitative comparison measures

#### Decision Making
- Lines ranked highly by multiple formulas are more likely to be faulty
- Use correlation to understand formula similarities
- Consider formula diversity for robust fault localization

### Formula Performance Tab

Advanced performance analysis and benchmarking:

#### Metrics
- **Effectiveness Analysis**: How well do formulas identify faults?
- **Ranking Quality**: Top-N analysis for different formulas
- **Performance Comparison**: Relative effectiveness measures
- **Export Capabilities**: Generate detailed performance reports

#### Research Applications
- Compare formula effectiveness on your specific codebase
- Identify which formulas work best for your project type
- Export data for further analysis or reporting

## 🎯 Best Practices

### Test Suite Preparation

#### Ensure Adequate Test Coverage
```bash
# Check current coverage
coverage run -m pytest
coverage report

# Aim for >70% line coverage for effective FL
# Focus on critical business logic
```

#### Include Failing Tests
- Fault localization requires failing tests to be effective
- Ensure you have tests that exercise the buggy code
- At least 2-3 failing tests provide better FL precision

#### Organize Test Structure
```
tests/
├── unit/           # Unit tests for individual functions
├── integration/    # Integration tests for component interaction
└── end_to_end/     # Full workflow tests
```

### Project Structure Optimization

#### Recommended Directory Layout
```
your_project/
├── src/                    # Source code
│   └── your_package/
├── tests/                  # Test files
├── pyfault.conf           # PyFault configuration
└── requirements.txt       # Dependencies
```

#### File Naming Conventions
- Use clear, descriptive names for source files
- Follow consistent naming patterns
- Avoid deeply nested directory structures when possible

### Configuration Best Practices

#### Ignore Patterns
```ini
[test]
ignore = */__init__.py, */migrations/*, */vendor/*, */build/*
```

#### Omit Patterns
```ini
[test]
omit = */__init__.py, */tests/*, */venv/*, */.venv/*, */site-packages/*
```

#### Formula Selection
```ini
[fl]
# Start with these proven formulas
formulas = ochiai, tarantula, jaccard, dstar2

# For research or comparison, add more
# formulas = ochiai, tarantula, jaccard, dstar2, dstar3
```

### Workflow Recommendations

#### Development Workflow
1. **Red**: Write a failing test that exposes the bug
2. **Analyze**: Run PyFault to identify suspicious areas
3. **Focus**: Investigate the highest-ranking suspicious lines
4. **Green**: Fix the bug and verify tests pass
5. **Refactor**: Clean up code while maintaining test coverage

#### CI/CD Integration
```yaml
# Example GitHub Actions workflow
name: Fault Localization Analysis
on: [push, pull_request]

jobs:
  fl-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pyfault[ui]
          pip install -r requirements.txt
      - name: Run fault localization
        run: pyfault run --source-dir src --output fl_report.json
      - name: Upload FL report
        uses: actions/upload-artifact@v3
        with:
          name: fault-localization-report
          path: fl_report.json
```

### Interpreting Results

#### High Suspiciousness Scores (>0.7)
- **Action**: Investigate immediately
- **Likelihood**: High probability of containing the fault
- **Strategy**: Focus debugging efforts here first

#### Medium Suspiciousness Scores (0.3-0.7)
- **Action**: Secondary investigation targets
- **Likelihood**: Moderate probability of fault involvement
- **Strategy**: Investigate if high-suspicion areas don't reveal the fault

#### Low Suspiciousness Scores (<0.3)
- **Action**: Low priority for immediate investigation
- **Likelihood**: Less likely to contain the fault
- **Strategy**: Consider only if other areas are exhausted

#### Formula Consensus
- Lines ranked highly by multiple formulas are more reliable
- Focus on areas where 3+ formulas agree on high suspiciousness
- Use formula disagreement to identify edge cases

## 🔍 Troubleshooting

### Common Issues and Solutions

#### No Failing Tests
**Problem**: "No failing tests - fault localization cannot be performed"

**Solutions:**
1. Ensure you have tests that actually fail
2. Check that pytest is discovering your tests correctly
3. Verify test files are in the expected location

```bash
# Debug test discovery
pytest --collect-only
```

#### Low Coverage
**Problem**: "Low coverage - fault localization effectiveness limited"

**Solutions:**
1. Add more comprehensive tests
2. Focus on testing critical business logic
3. Use coverage reports to identify gaps

```bash
# Generate detailed coverage report
coverage run -m pytest
coverage html
# Open htmlcov/index.html
```

#### No Suspicious Lines
**Problem**: All suspiciousness scores are very low

**Possible Causes:**
1. Tests might not be exercising the buggy code
2. Bug might be in untested code paths
3. Test failures might not be related to code coverage

**Solutions:**
1. Add tests that specifically exercise the suspected buggy areas
2. Ensure failing tests cover different code paths than passing tests
3. Review test quality and relevance

#### Dashboard Won't Load
**Problem**: Dashboard fails to start or shows errors

**Solutions:**
1. Ensure UI dependencies are installed: `pip install pyfault[ui]`
2. Check that the report file exists and is valid JSON
3. Try a different port: `pyfault ui --port 8080`

#### Memory Issues with Large Projects
**Problem**: PyFault runs out of memory on large codebases

**Solutions:**
1. Use more specific source directories
2. Increase omit patterns to exclude unnecessary files
3. Run analysis on smaller subsets of your codebase

### Debug Mode

Enable verbose output for detailed debugging:

```bash
pyfault run --verbose
```

This provides:
- Detailed test execution logs
- Coverage collection progress
- Formula calculation details
- Error stack traces

### Performance Optimization

#### For Large Projects
```ini
[test]
# Be specific about what to analyze
source_dir = src/core  # Instead of entire src/
omit = */tests/*, */vendor/*, */migrations/*, */__pycache__/*

[fl]
# Use fewer formulas initially
formulas = ochiai, tarantula
```

#### For Faster Iterations
```bash
# Run only specific tests during development
pyfault run --test-filter "test_feature_x" --source-dir src/feature_x
```

## 📊 Advanced Usage

### Custom Formula Implementation

You can extend PyFault with custom SBFL formulas:

```python
from pyfault.formulas import SBFLFormula

class MyCustomFormula(SBFLFormula):
    def __init__(self):
        super().__init__("my_custom")
    
    def calculate(self, n_cf, n_nf, n_cp, n_np):
        # Your custom formula logic here
        if n_cf == 0:
            return 0.0
        return n_cf / (n_cf + n_cp + 1)
```

### Programmatic Usage

Use PyFault in your own Python scripts:

```python
from pyfault.test import TestRunner, TestConfig
from pyfault.fl import FLEngine, FLConfig
import json

# Configure and run tests
test_config = TestConfig(source_dir="src", output_file="coverage.json")
runner = TestRunner(test_config)
result = runner.run_tests()

# Run fault localization
fl_config = FLConfig(formulas=["ochiai", "tarantula"])
engine = FLEngine(fl_config)
engine.calculate_suspiciousness("coverage.json", "report.json")

# Load and analyze results
with open("report.json") as f:
    report = json.load(f)
    
# Extract top suspicious lines
for file_path, file_data in report["files"].items():
    ochiai_scores = file_data["suspiciousness"]["ochiai"]
    top_lines = sorted(ochiai_scores.items(), 
                      key=lambda x: x[1], reverse=True)[:5]
    print(f"{file_path}: {top_lines}")
```

### Integration with Other Tools

#### IDE Integration
Export results for IDE highlighting:

```python
import json

def export_for_ide(report_file, formula="ochiai", threshold=0.5):
    with open(report_file) as f:
        data = json.load(f)
    
    highlights = {}
    for file_path, file_data in data["files"].items():
        scores = file_data["suspiciousness"][formula]
        highlights[file_path] = [
            int(line) for line, score in scores.items() 
            if score >= threshold
        ]
    
    return highlights
```

#### Continuous Integration
Generate reports for CI systems:

```bash
# Generate machine-readable output
pyfault run --output ci_report.json
python -c "
import json
with open('ci_report.json') as f:
    data = json.load(f)
print(f'Analyzed {len(data[\"files\"])} files')
print(f'Found {data[\"totals\"][\"test_statistics\"][\"failed_tests\"]} failing tests')
"
```

This user guide should help you effectively use PyFault for fault localization in your Python projects. For more advanced topics and API details, refer to the API Reference and Architecture documentation.
