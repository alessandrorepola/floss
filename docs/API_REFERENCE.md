# PyFault API Reference

This document provides a comprehensive API reference for PyFault's modules, classes, and functions.

## 📦 Module Overview

PyFault is organized into several key modules:

- **`pyfault.test`**: Test execution and coverage collection
- **`pyfault.fl`**: Fault localization engine and data structures
- **`pyfault.formulas`**: SBFL formula implementations
- **`pyfault.cli`**: Command-line interface
- **`pyfault.ui`**: Interactive dashboard and visualizations

## 🧪 Test Module (`pyfault.test`)

### TestRunner

Main class for executing tests and collecting coverage data.

```python
class TestRunner:
    """Execute tests with enhanced coverage collection for fault localization."""
    
    def __init__(self, config: TestConfig):
        """Initialize test runner with configuration."""
        pass
    
    def run_tests(self, test_filter: Optional[str] = None) -> TestResult:
        """
        Execute tests with coverage collection.
        
        Args:
            test_filter: Optional pytest -k pattern for filtering tests
            
        Returns:
            TestResult containing coverage data and test outcomes
        """
        pass
```

#### Methods

##### `run_tests(test_filter: Optional[str] = None) -> TestResult`

Executes the test suite with comprehensive coverage collection.

**Parameters:**
- `test_filter` (Optional[str]): pytest -k pattern for selective test execution

**Returns:**
- `TestResult`: Object containing coverage data, test outcomes, and metadata

**Example:**
```python
from pyfault.test import TestRunner, TestConfig

config = TestConfig(source_dir="src", output_file="coverage.json")
runner = TestRunner(config)
result = runner.run_tests(test_filter="test_critical")

print(f"Passed tests: {len(result.passed_tests)}")
print(f"Failed tests: {len(result.failed_tests)}")
```

### TestConfig

Configuration class for test execution parameters.

```python
@dataclass
class TestConfig:
    """Configuration for test execution."""
    
    source_dir: str = "."
    test_dir: Optional[str] = None
    output_file: str = "coverage.json"
    ignore_patterns: Optional[List[str]] = None
    omit_patterns: Optional[List[str]] = None
```

#### Attributes

- **`source_dir`** (str): Directory containing source code to analyze (default: ".")
- **`test_dir`** (Optional[str]): Directory containing test files (auto-detected if None)
- **`output_file`** (str): Output file for coverage data (default: "coverage.json")
- **`ignore_patterns`** (Optional[List[str]]): Patterns to ignore during test discovery
- **`omit_patterns`** (Optional[List[str]]): Patterns to omit from coverage analysis

#### Methods

##### `from_file(config_file: str = "pyfault.conf") -> TestConfig`

Load configuration from a file.

**Parameters:**
- `config_file` (str): Path to configuration file (default: "pyfault.conf")

**Returns:**
- `TestConfig`: Configuration object with loaded settings

**Example:**
```python
config = TestConfig.from_file("custom_config.conf")
```

##### `get_coveragerc_content() -> str`

Generate .coveragerc content with required settings.

**Returns:**
- `str`: Content for .coveragerc file

##### `write_coveragerc(path: str = ".coveragerc") -> None`

Write .coveragerc file with configuration.

**Parameters:**
- `path` (str): Path for .coveragerc file (default: ".coveragerc")

### TestResult

Data structure containing test execution results.

```python
@dataclass
class TestResult:
    """Results from test execution with coverage."""
    
    coverage_data: Dict[str, Any]
    passed_tests: List[str]
    failed_tests: List[str]
    skipped_tests: List[str]
    execution_time: float
```

#### Attributes

- **`coverage_data`** (Dict[str, Any]): Detailed coverage information
- **`passed_tests`** (List[str]): Names of tests that passed
- **`failed_tests`** (List[str]): Names of tests that failed
- **`skipped_tests`** (List[str]): Names of tests that were skipped
- **`execution_time`** (float): Total test execution time in seconds

## 🎯 Fault Localization Module (`pyfault.fl`)

### FLEngine

Main engine for fault localization processing.

```python
class FLEngine:
    """Engine for calculating fault localization suspiciousness scores."""
    
    def __init__(self, config: FLConfig):
        """Initialize FL engine with configuration."""
        pass
    
    def calculate_suspiciousness(self, input_file: str, output_file: str) -> None:
        """
        Calculate suspiciousness scores and generate report.
        
        Args:
            input_file: Path to coverage data file
            output_file: Path for output report file
        """
        pass
```

#### Methods

##### `calculate_suspiciousness(input_file: str, output_file: str) -> None`

Main method for calculating suspiciousness scores using SBFL formulas.

**Parameters:**
- `input_file` (str): Path to input coverage data file
- `output_file` (str): Path for output fault localization report

**Example:**
```python
from pyfault.fl import FLEngine, FLConfig

config = FLConfig(formulas=["ochiai", "tarantula"])
engine = FLEngine(config)
engine.calculate_suspiciousness("coverage.json", "report.json")
```

### FLConfig

Configuration class for fault localization parameters.

```python
@dataclass
class FLConfig:
    """Configuration for fault localization."""
    
    input_file: str = "coverage.json"
    output_file: str = "report.json"
    formulas: Optional[List[str]] = None
```

#### Attributes

- **`input_file`** (str): Input coverage file path (default: "coverage.json")
- **`output_file`** (str): Output report file path (default: "report.json")
- **`formulas`** (Optional[List[str]]): List of SBFL formulas to apply

#### Methods

##### `from_file(config_file: str) -> FLConfig`

Load configuration from a file.

**Parameters:**
- `config_file` (str): Path to configuration file

**Returns:**
- `FLConfig`: Configuration object with loaded settings

### FLData

Data structure for fault localization information.

```python
@dataclass
class FLData:
    """Data structure for fault localization analysis."""
    
    coverage_matrix: Dict[str, Dict[int, List[str]]]
    test_outcomes: Dict[str, str]
    file_metadata: Dict[str, Dict[str, Any]]
    suspiciousness_scores: Dict[str, Dict[str, Dict[int, float]]]
```

#### Attributes

- **`coverage_matrix`** (Dict): Mapping of files to line coverage by tests
- **`test_outcomes`** (Dict): Test names mapped to outcomes (passed/failed/skipped)
- **`file_metadata`** (Dict): Metadata about analyzed files
- **`suspiciousness_scores`** (Dict): Calculated suspiciousness scores by formula and file

## 🧮 Formulas Module (`pyfault.formulas`)

### SBFLFormula

Abstract base class for all SBFL formula implementations.

```python
class SBFLFormula:
    """Abstract base class for SBFL formulas."""
    
    def __init__(self, name: str):
        """Initialize formula with name."""
        self.name = name
    
    @abstractmethod
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """
        Calculate suspiciousness score.
        
        Args:
            n_cf: Number of failed tests covering the line
            n_nf: Number of failed tests not covering the line
            n_cp: Number of passed tests covering the line
            n_np: Number of passed tests not covering the line
            
        Returns:
            Suspiciousness score (0.0 to 1.0)
        """
        pass
```

#### Methods

##### `calculate(n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float`

Abstract method for calculating suspiciousness scores.

**Parameters:**
- `n_cf` (int): Number of failed tests covering the line
- `n_nf` (int): Number of failed tests not covering the line
- `n_cp` (int): Number of passed tests covering the line
- `n_np` (int): Number of passed tests not covering the line

**Returns:**
- `float`: Suspiciousness score between 0.0 and 1.0

### Concrete Formula Classes

#### OchiaiFormula

Implementation of the Ochiai similarity coefficient.

```python
class OchiaiFormula(SBFLFormula):
    """Ochiai similarity coefficient formula."""
    
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """Calculate Ochiai suspiciousness score."""
        pass
```

**Formula:** `n_cf / sqrt((n_cf + n_nf) * (n_cf + n_cp))`

**Example:**
```python
formula = OchiaiFormula()
score = formula.calculate(n_cf=5, n_nf=3, n_cp=2, n_np=10)
```

#### TarantulaFormula

Implementation of the Tarantula formula.

```python
class TarantulaFormula(SBFLFormula):
    """Tarantula formula for fault localization."""
    
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """Calculate Tarantula suspiciousness score."""
        pass
```

**Formula:** `(n_cf / (n_cf + n_nf)) / ((n_cf / (n_cf + n_nf)) + (n_cp / (n_cp + n_np)))`

#### JaccardFormula

Implementation of the Jaccard similarity coefficient.

```python
class JaccardFormula(SBFLFormula):
    """Jaccard similarity coefficient formula."""
    
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """Calculate Jaccard suspiciousness score."""
        pass
```

**Formula:** `n_cf / (n_cf + n_nf + n_cp)`

#### DStarFormula

Implementation of the D* formula.

```python
class DStarFormula(SBFLFormula):
    """D* formula for fault localization."""
    
    def __init__(self, star: int = 2, name: Optional[str] = None):
        """Initialize D* formula with exponent."""
        pass
    
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """Calculate D* suspiciousness score."""
        pass
```

**Formula:** `n_cf^star / (n_cp + n_nf)`

**Parameters:**
- `star` (int): Exponent value (typically 2 or 3)

### Utility Functions

#### `safe_divide(numerator: float, denominator: float) -> float`

Safely divide two numbers, handling division by zero.

**Parameters:**
- `numerator` (float): Numerator value
- `denominator` (float): Denominator value

**Returns:**
- `float`: Division result or 0.0 if denominator is zero

#### `safe_sqrt(value: float) -> float`

Safely calculate square root, handling negative values.

**Parameters:**
- `value` (float): Input value

**Returns:**
- `float`: Square root or 0.0 if value is negative

## 🖥️ CLI Module (`pyfault.cli`)

### Main Functions

#### `main()`

Entry point for the PyFault CLI application.

```python
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """PyFault: Spectrum-Based Fault Localization for Python"""
    pass
```

#### Command Functions

##### `test()`

Command for test execution with coverage collection.

```python
@main.command()
@click.option('--source-dir', '-s', default='.')
@click.option('--test-dir', '-t')
@click.option('--output', '-o', default='coverage.json')
@click.option('--test-filter', '-k')
@click.option('--ignore', multiple=True)
@click.option('--omit', multiple=True)
@click.option('--config', '-c', default='pyfault.conf')
@click.pass_context
def test(ctx, source_dir, test_dir, output, test_filter, ignore, omit, config):
    """Run tests with coverage collection."""
    pass
```

##### `fl()`

Command for fault localization calculation.

```python
@main.command()
@click.option('--input', '-i', default='coverage.json')
@click.option('--output', '-o', default='report.json')
@click.option('--formulas', '-f', multiple=True)
@click.option('--config', '-c', default='pyfault.conf')
@click.pass_context
def fl(ctx, input, output, formulas, config):
    """Calculate fault localization suspiciousness scores."""
    pass
```

##### `run()`

Command for complete pipeline execution.

```python
@main.command()
@click.option('--source-dir', '-s', default='.')
@click.option('--test-dir', '-t')
@click.option('--output', '-o', default='report.json')
@click.option('--test-filter', '-k')
@click.option('--ignore', multiple=True)
@click.option('--omit', multiple=True)
@click.option('--formulas', '-f', multiple=True)
@click.option('--config', '-c', default='pyfault.conf')
@click.pass_context
def run(ctx, source_dir, test_dir, output, test_filter, ignore, omit, formulas, config):
    """Run complete fault localization pipeline."""
    pass
```

##### `ui()`

Command for launching the interactive dashboard.

```python
@main.command()
@click.option('--report', '-r', default='report.json')
@click.option('--port', '-p', default=8501)
@click.option('--no-open', is_flag=True)
@click.pass_context
def ui(ctx, report, port, no_open):
    """Launch PyFault dashboard for result visualization."""
    pass
```

## 🎨 UI Module (`pyfault.ui`)

### Dashboard Functions

#### `launch_dashboard()`

Main function for launching the Streamlit dashboard.

```python
def launch_dashboard(report_file: str = "report.json", 
                    port: int = 8501, 
                    auto_open: bool = True) -> None:
    """
    Launch the dashboard.
    
    Args:
        report_file: Path to fault localization report
        port: Port for the dashboard server
        auto_open: Whether to automatically open browser
    """
    pass
```

#### Visualization Functions

##### `show_overview(data: Dict[str, Any], formula: str)`

Display comprehensive overview with key metrics.

##### `show_source_code(data: Dict[str, Any], formula: str)`

Show interactive source code viewer with suspiciousness highlighting.

##### `show_coverage_matrix(data: Dict[str, Any], formula: str)`

Display test-to-fault coverage matrix visualization.

##### `show_treemap(data: Dict[str, Any], formula: str)`

Create hierarchical treemap visualization.

##### `show_sunburst(data: Dict[str, Any], formula: str)`

Generate sunburst chart for project structure.

##### `show_formula_comparison(data: Dict[str, Any], formulas: List[str])`

Compare different SBFL formulas side-by-side.

##### `show_formula_performance(data: Dict[str, Any], formulas: List[str])`

Analyze and display formula performance metrics.

### Data Structures

#### `FormulaStats`

Statistics for a specific formula.

```python
class FormulaStats(NamedTuple):
    """Statistics for a specific formula."""
    min_score: float
    max_score: float
    mean_score: float
    std_score: float
    range_score: float
    all_scores: List[float]
```

#### `FileStats`

Statistics for a file's suspiciousness.

```python
class FileStats(NamedTuple):
    """Statistics for a file's suspiciousness."""
    file_path: str
    max_score: float
    avg_score: float
    suspicious_statements: int
    total_statements: int
    suspicious_statements_pct: float
```

## 🔧 Utility Functions

### Configuration Utilities

#### `load_config(config_file: str) -> Dict[str, Any]`

Load configuration from INI file.

**Parameters:**
- `config_file` (str): Path to configuration file

**Returns:**
- `Dict[str, Any]`: Parsed configuration data

### Data Processing Utilities

#### `normalize_scores(scores: List[float]) -> List[float]`

Normalize suspiciousness scores to 0-1 range.

**Parameters:**
- `scores` (List[float]): Raw suspiciousness scores

**Returns:**
- `List[float]`: Normalized scores

#### `calculate_statistics(scores: List[float]) -> Dict[str, float]`

Calculate statistical metrics for score distribution.

**Parameters:**
- `scores` (List[float]): Suspiciousness scores

**Returns:**
- `Dict[str, float]`: Statistical metrics (mean, std, min, max, etc.)

## 📊 Data Formats

### Coverage Data Format

```json
{
  "meta": {
    "version": "coverage.py version",
    "timestamp": "2025-01-01T00:00:00",
    "command_line": "coverage run -m pytest"
  },
  "files": {
    "src/module.py": {
      "executed_lines": [1, 2, 5, 7, 10],
      "summary": {
        "covered_lines": 5,
        "num_statements": 15,
        "percent_covered": 33.33
      },
      "contexts": {
        "test_function_a": [1, 2],
        "test_function_b": [5, 7, 10]
      }
    }
  },
  "totals": {
    "covered_lines": 5,
    "num_statements": 15,
    "percent_covered": 33.33
  }
}
```

### FL Report Format

```json
{
  "meta": {
    "timestamp": "2025-01-01T00:00:00",
    "pyfault_version": "0.1.0",
    "formulas_used": ["ochiai", "tarantula"],
    "source_files_analyzed": 10
  },
  "totals": {
    "test_statistics": {
      "total_tests": 25,
      "passed_tests": 20,
      "failed_tests": 5,
      "skipped_tests": 0
    },
    "analysis_statistics": {
      "files_analyzed": 10,
      "total_lines_with_scores": 150
    },
    "sbfl_formulas": ["ochiai", "tarantula"]
  },
  "files": {
    "src/module.py": {
      "suspiciousness": {
        "ochiai": {
          "1": 0.857,
          "2": 0.654,
          "5": 0.123
        },
        "tarantula": {
          "1": 0.923,
          "2": 0.786,
          "5": 0.234
        }
      },
      "coverage_data": {
        "line_coverage": [1, 2, 5, 7, 10],
        "test_contexts": {...}
      }
    }
  }
}
```

## 🚀 Usage Examples

### Basic API Usage

```python
from pyfault.test import TestRunner, TestConfig
from pyfault.fl import FLEngine, FLConfig

# Configure and run tests
test_config = TestConfig(
    source_dir="src",
    test_dir="tests",
    output_file="coverage.json"
)
runner = TestRunner(test_config)
result = runner.run_tests()

# Configure and run fault localization
fl_config = FLConfig(
    input_file="coverage.json",
    output_file="report.json",
    formulas=["ochiai", "tarantula"]
)
engine = FLEngine(fl_config)
engine.calculate_suspiciousness("coverage.json", "report.json")
```

### Custom Formula Implementation

```python
from pyfault.formulas import SBFLFormula

class CustomFormula(SBFLFormula):
    def __init__(self):
        super().__init__("custom")
    
    def calculate(self, n_cf, n_nf, n_cp, n_np):
        # Custom formula logic
        if n_cf == 0:
            return 0.0
        return n_cf / (n_cf + n_cp + 1)

# Register and use custom formula
formula = CustomFormula()
score = formula.calculate(5, 3, 2, 10)
```

### Dashboard Integration

```python
from pyfault.ui import launch_dashboard

# Launch dashboard with custom settings
launch_dashboard(
    report_file="custom_report.json",
    port=8502,
    auto_open=False
)
```

This API reference provides comprehensive documentation for all public interfaces in PyFault. For implementation details and internal APIs, refer to the source code and architecture documentation.
