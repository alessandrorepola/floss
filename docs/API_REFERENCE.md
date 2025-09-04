# floss API Reference

This document provides comprehensive API documentation for floss's programmatic interfaces.

## Table of Contents

- [Core Classes](#core-classes)
- [Configuration Classes](#configuration-classes)
- [SBFL Formulas](#sbfl-formulas)
- [Data Structures](#data-structures)
- [CLI Integration](#cli-integration)
- [Dashboard Integration](#dashboard-integration)
- [Extensions and Customization](#extensions-and-customization)

## Core Classes

### TestRunner

The `TestRunner` class executes tests with coverage collection and provides comprehensive test results.

```python
from floss.test import TestRunner, TestConfig

class TestRunner:
    """Executes tests with pytest and coverage collection."""

    def __init__(self, config: TestConfig) -> None:
        """Initialize test runner with configuration."""

    def run_tests(self, test_filter: Optional[str] = None) -> TestResult:
        """
        Run tests and collect coverage with context information.

        Args:
            test_filter: Optional pytest -k filter pattern

        Returns:
            TestResult object containing coverage data and test outcomes

        Raises:
            RuntimeError: If pytest execution fails
        """
```

#### Example Usage

```python
from floss.test import TestRunner, TestConfig

# Create configuration
config = TestConfig(
    source_dir="src",
    test_dir="tests",
    output_file="coverage.json"
)

# Initialize runner
runner = TestRunner(config)

# Run tests
result = runner.run_tests()

# Access results
print(f"Passed tests: {len(result.passed_tests)}")
print(f"Failed tests: {len(result.failed_tests)}")
print(f"Coverage data: {result.coverage_data}")
```

### FLEngine

The `FLEngine` class calculates fault localization suspiciousness scores using SBFL formulas.

```python
from floss.fl import FLEngine, FLConfig

class FLEngine:
    """Engine for calculating fault localization suspiciousness scores."""

    # Available formulas registry
    AVAILABLE_FORMULAS = {
        "ochiai": OchiaiFormula(),
        "tarantula": TarantulaFormula(),
        "jaccard": JaccardFormula(),
        "dstar2": DStarFormula(star=2),
        "dstar3": DStarFormula(star=3),
        "kulczynski2": Kulczynski2Formula(),
        "naish1": Naish1Formula(),
        "russellrao": RussellRaoFormula(),
        "sorensendice": SorensenDiceFormula(),
        "sbi": SBIFormula(),
    }

    def __init__(self, config: FLConfig) -> None:
        """Initialize FL engine with configuration."""

    def calculate_suspiciousness(self, input_file: str, output_file: str) -> None:
        """
        Calculate suspiciousness scores and generate report.

        Args:
            input_file: Path to coverage JSON file
            output_file: Path to output report JSON file

        Raises:
            FileNotFoundError: If input file doesn't exist
            json.JSONDecodeError: If input file is malformed
        """
```

#### Example Usage

```python
from floss.fl import FLEngine, FLConfig

# Create configuration
config = FLConfig(
    input_file="coverage.json",
    output_file="report.json",
    formulas=["ochiai", "tarantula", "dstar2"]
)

# Initialize engine
engine = FLEngine(config)

# Calculate suspiciousness
engine.calculate_suspiciousness("coverage.json", "report.json")
```

## Configuration Classes

### TestConfig

Configuration class for test execution parameters.

```python
from floss.test.config import TestConfig

class TestConfig:
    """Configuration for test execution."""

    def __init__(
        self,
        source_dir: str = ".",
        test_dir: Optional[str] = None,
        output_file: str = "coverage.json",
        ignore_patterns: Optional[List[str]] = None,
        omit_patterns: Optional[List[str]] = None
    ) -> None:
        """
        Initialize test configuration.

        Args:
            source_dir: Source code directory to analyze
            test_dir: Test directory (auto-detected if None)
            output_file: Output file for coverage data
            ignore_patterns: File patterns to ignore for test discovery
            omit_patterns: File patterns to omit from coverage
        """

    @classmethod
    def from_file(cls, config_file: str) -> "TestConfig":
        """
        Load configuration from file.

        Args:
            config_file: Path to configuration file

        Returns:
            TestConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is malformed
        """

    def write_coveragerc(self, filename: str) -> None:
        """
        Write coverage configuration file.

        Args:
            filename: Path to coverage config file
        """
```

#### Example Usage

```python
from floss.test.config import TestConfig

# Create from parameters
config = TestConfig(
    source_dir="src",
    test_dir="tests",
    ignore_patterns=["*/migrations/*", "*/vendor/*"],
    omit_patterns=["*/__init__.py", "*/conftest.py"]
)

# Load from file
config = TestConfig.from_file("floss.conf")

# Access properties
print(f"Source directory: {config.source_dir}")
print(f"Test directory: {config.test_dir}")
print(f"Output file: {config.output_file}")
```

### FLConfig

Configuration class for fault localization parameters.

```python
from floss.fl.config import FLConfig

class FLConfig:
    """Configuration for fault localization."""

    def __init__(
        self,
        input_file: str = "coverage.json",
        output_file: str = "report.json",
        formulas: Optional[List[str]] = None
    ) -> None:
        """
        Initialize FL configuration.

        Args:
            input_file: Input coverage file
            output_file: Output report file
            formulas: List of SBFL formulas to use
        """

    @classmethod
    def from_file(cls, config_file: str) -> "FLConfig":
        """
        Load configuration from file.

        Args:
            config_file: Path to configuration file

        Returns:
            FLConfig instance
        """
```

#### Example Usage

```python
from floss.fl.config import FLConfig

# Create from parameters
config = FLConfig(
    input_file="my_coverage.json",
    output_file="my_report.json",
    formulas=["ochiai", "tarantula", "jaccard"]
)

# Load from file
config = FLConfig.from_file("floss.conf")

# Access properties
print(f"Input file: {config.input_file}")
print(f"Output file: {config.output_file}")
print(f"Formulas: {config.formulas}")
```

## SBFL Formulas

### Base Formula Class

All SBFL formulas inherit from the `SBFLFormula` abstract base class.

```python
from floss.formulas.base import SBFLFormula

class SBFLFormula(ABC):
    """Abstract base class for SBFL formulas."""

    def __init__(self, name: Optional[str] = None) -> None:
        """Initialize formula with optional custom name."""

    @property
    def name(self) -> str:
        """Get the formula name."""

    @abstractmethod
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """
        Calculate suspiciousness score for a code element.

        Args:
            n_cf: Number of failed tests covering the element
            n_nf: Number of failed tests NOT covering the element
            n_cp: Number of passed tests covering the element
            n_np: Number of passed tests NOT covering the element

        Returns:
            Suspiciousness score (typically between 0 and 1)
        """
```

### Implemented Formulas

#### OchiaiFormula

```python
from floss.formulas import OchiaiFormula

formula = OchiaiFormula()
score = formula.calculate(n_cf=3, n_nf=2, n_cp=1, n_np=4)
print(f"Ochiai score: {score}")
```

**Formula**: `n_cf / sqrt((n_cf + n_nf) * (n_cf + n_cp))`

**Best for**: General-purpose fault localization, most effective across scenarios

#### TarantulaFormula

```python
from floss.formulas import TarantulaFormula

formula = TarantulaFormula()
score = formula.calculate(n_cf=3, n_nf=2, n_cp=1, n_np=4)
print(f"Tarantula score: {score}")
```

**Formula**: `(n_cf / (n_cf + n_nf)) / ((n_cf / (n_cf + n_nf)) + (n_cp / (n_cp + n_np)))`

**Best for**: Baseline comparisons, well-studied formula

#### JaccardFormula

```python
from floss.formulas import JaccardFormula

formula = JaccardFormula()
score = formula.calculate(n_cf=3, n_nf=2, n_cp=1, n_np=4)
print(f"Jaccard score: {score}")
```

**Formula**: `n_cf / (n_cf + n_nf + n_cp)`

**Best for**: Simple and interpretable results

#### DStarFormula

```python
from floss.formulas import DStarFormula

# D* with exponent 2
formula = DStarFormula(star=2)
score = formula.calculate(n_cf=3, n_nf=2, n_cp=1, n_np=4)
print(f"D*2 score: {score}")

# D* with exponent 3
formula = DStarFormula(star=3)
score = formula.calculate(n_cf=3, n_nf=2, n_cp=1, n_np=4)
print(f"D*3 score: {score}")
```

**Formula**: `n_cf^star / (n_cp + n_nf)`

**Best for**: Projects with many passing tests

### Custom Formula Implementation

```python
from floss.formulas.base import SBFLFormula, safe_divide

class CustomFormula(SBFLFormula):
    """Custom SBFL formula implementation."""

    def __init__(self, parameter: float = 1.0):
        super().__init__("custom")
        self.parameter = parameter

    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """Implement custom calculation logic."""
        if n_cf == 0:
            return 0.0

        # Example: weighted combination
        numerator = n_cf * self.parameter
        denominator = (n_cf + n_nf) + (n_cp * 0.5)

        return safe_divide(numerator, denominator)

# Usage
custom_formula = CustomFormula(parameter=2.0)
score = custom_formula.calculate(3, 2, 1, 4)
```

### Formula Utilities

```python
from floss.formulas.base import safe_divide, safe_sqrt

# Safe division (returns 0.0 if denominator is 0)
result = safe_divide(10, 0)  # Returns 0.0

# Safe square root (returns 0.0 if value is negative)
result = safe_sqrt(-5)  # Returns 0.0
result = safe_sqrt(16)   # Returns 4.0
```

## Data Structures

### TestResult

Result object returned by `TestRunner.run_tests()`.

```python
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class TestResult:
    """Result of test execution."""

    coverage_data: Dict[str, Any]  # Enhanced coverage JSON data
    failed_tests: List[str]        # List of failed test names
    passed_tests: List[str]        # List of passed test names
    skipped_tests: List[str]       # List of skipped test names
```

#### Example Usage

```python
result = runner.run_tests()

# Access test outcomes
print(f"Total tests: {len(result.passed_tests) + len(result.failed_tests) + len(result.skipped_tests)}")
print(f"Pass rate: {len(result.passed_tests) / (len(result.passed_tests) + len(result.failed_tests)):.2%}")

# Access coverage data
files_data = result.coverage_data.get("files", {})
for file_path, file_data in files_data.items():
    executed_lines = file_data.get("executed_lines", [])
    print(f"{file_path}: {len(executed_lines)} lines executed")
```

### CoverageData

Internal data structure for coverage analysis.

```python
from floss.fl.data import CoverageData

class CoverageData:
    """Coverage data abstraction for FL calculations."""

    def __init__(self, coverage_json: Dict[str, Any]) -> None:
        """Initialize from coverage JSON data."""

    @classmethod
    def from_json(cls, coverage_json: Dict[str, Any]) -> "CoverageData":
        """Create from JSON data."""

    def get_sbfl_params(self, line_key: str) -> Tuple[int, int, int, int]:
        """
        Get SBFL parameters for a specific line.

        Args:
            line_key: Line identifier (format: "file:line_number")

        Returns:
            Tuple of (n_cf, n_nf, n_cp, n_np)
        """

    @property
    def line_coverage(self) -> Dict[str, List[str]]:
        """Get line coverage mapping."""

    @property
    def test_outcomes(self) -> Dict[str, bool]:
        """Get test outcome mapping."""
```

#### Example Usage

```python
import json
from floss.fl.data import CoverageData

# Load coverage data
with open("coverage.json") as f:
    coverage_json = json.load(f)

# Create coverage data object
coverage_data = CoverageData.from_json(coverage_json)

# Get SBFL parameters for specific line
n_cf, n_nf, n_cp, n_np = coverage_data.get_sbfl_params("src/module.py:42")
print(f"Line src/module.py:42 - CF:{n_cf}, NF:{n_nf}, CP:{n_cp}, NP:{n_np}")

# Iterate over all covered lines
for line_key in coverage_data.line_coverage:
    params = coverage_data.get_sbfl_params(line_key)
    print(f"{line_key}: {params}")
```

## CLI Integration

### Programmatic CLI Execution

```python
import subprocess
import json
from pathlib import Path

def run_floss_analysis(source_dir: str, test_dir: str, output_file: str) -> Dict:
    """Run floss analysis programmatically."""

    # Build command
    cmd = [
        "floss", "run",
        "--source-dir", source_dir,
        "--test-dir", test_dir,
        "--output", output_file
    ]

    # Execute
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"floss failed: {result.stderr}")

    # Load results
    with open(output_file) as f:
        return json.load(f)

# Usage
try:
    report = run_floss_analysis("src", "tests", "analysis_report.json")
    print(f"Analysis completed: {report['totals']['total_tests']} tests analyzed")
except RuntimeError as e:
    print(f"Analysis failed: {e}")
```

### Click Context Integration

```python
from click.testing import CliRunner
from floss.cli.main import main

def test_cli_integration():
    """Test CLI integration."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create test files
        # ... setup code ...

        # Test 'test' command
        result = runner.invoke(main, ['test', '--source-dir', 'src'])
        assert result.exit_code == 0

        # Test 'fl' command
        result = runner.invoke(main, ['fl', '--input', 'coverage.json'])
        assert result.exit_code == 0

        # Test 'run' command
        result = runner.invoke(main, ['run'])
        assert result.exit_code == 0
```

## Dashboard Integration

### Programmatic Dashboard Launch

```python
from floss.ui.dashboard import launch_dashboard
import threading
import time

def start_dashboard_background(report_file: str, port: int = 8501):
    """Start dashboard in background thread."""

    def run_dashboard():
        launch_dashboard(
            report_file=report_file,
            port=port,
            auto_open=False  # Don't auto-open browser
        )

    # Start in background thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()

    # Wait for startup
    time.sleep(2)

    return f"http://localhost:{port}"

# Usage
dashboard_url = start_dashboard_background("report.json", 8502)
print(f"Dashboard available at: {dashboard_url}")
```

### Custom Dashboard Components

```python
import streamlit as st
import json
from floss.ui.dashboard import calculate_formula_statistics

def create_custom_summary(report_file: str):
    """Create custom summary component."""

    # Load data
    with open(report_file) as f:
        data = json.load(f)

    # Calculate statistics
    ochiai_stats = calculate_formula_statistics(data, "ochiai")

    # Display summary
    st.write("## Custom Project Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tests", data.get("totals", {}).get("total_tests", 0))

    with col2:
        st.metric("Failed Tests", data.get("totals", {}).get("failed_tests", 0))

    with col3:
        st.metric("Max Suspiciousness", f"{ochiai_stats.max_score:.3f}")

    # Custom visualization
    if ochiai_stats.all_scores:
        st.write("### Suspiciousness Distribution")
        st.histogram_chart(ochiai_stats.all_scores)

# Usage in Streamlit app
if __name__ == "__main__":
    st.set_page_config(page_title="Custom floss Dashboard")

    uploaded_file = st.file_uploader("Upload floss Report", type="json")
    if uploaded_file:
        # Save uploaded file
        with open("temp_report.json", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create custom summary
        create_custom_summary("temp_report.json")
```

## Extensions and Customization

### Custom Test Runner Integration

```python
from floss.test.config import TestConfig
from floss.test.runner import TestResult
import subprocess
import json

class CustomTestRunner:
    """Custom test runner for non-pytest frameworks."""

    def __init__(self, config: TestConfig):
        self.config = config

    def run_tests(self, test_filter: str = None) -> TestResult:
        """Run tests using custom framework."""

        # Example: unittest integration
        cmd = ["python", "-m", "unittest", "discover", "-s", self.config.test_dir]

        if test_filter:
            cmd.extend(["-k", test_filter])

        # Execute tests
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse results (custom logic needed)
        passed_tests, failed_tests = self._parse_unittest_output(result.stdout)

        # Generate coverage data (custom logic needed)
        coverage_data = self._generate_coverage_data()

        return TestResult(
            coverage_data=coverage_data,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=[]
        )

    def _parse_unittest_output(self, output: str):
        """Parse unittest output for test results."""
        # Implementation specific to unittest output format
        pass

    def _generate_coverage_data(self):
        """Generate coverage data in floss format."""
        # Implementation specific to coverage tool used
        pass
```

### Plugin System Example

```python
from typing import Dict, List
from floss.formulas.base import SBFLFormula

class FormulaPlugin:
    """Plugin interface for custom formulas."""

    def get_formulas(self) -> Dict[str, SBFLFormula]:
        """Return dictionary of formula name -> formula instance."""
        raise NotImplementedError

    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata."""
        raise NotImplementedError

class MyFormulaPlugin(FormulaPlugin):
    """Example custom formula plugin."""

    def get_formulas(self) -> Dict[str, SBFLFormula]:
        return {
            "my_formula": MyCustomFormula(),
            "experimental": ExperimentalFormula()
        }

    def get_metadata(self) -> Dict[str, str]:
        return {
            "name": "My Formula Plugin",
            "version": "1.0.0",
            "description": "Custom SBFL formulas for specific use cases"
        }

# Plugin registration
def register_formula_plugin(engine, plugin: FormulaPlugin):
    """Register plugin with FL engine."""
    formulas = plugin.get_formulas()
    for name, formula in formulas.items():
        engine.AVAILABLE_FORMULAS[name] = formula
```

### Configuration Extension

```python
from floss.test.config import TestConfig
from floss.fl.config import FLConfig
from typing import Optional, List

class ExtendedTestConfig(TestConfig):
    """Extended test configuration with additional options."""

    def __init__(
        self,
        source_dir: str = ".",
        test_dir: Optional[str] = None,
        output_file: str = "coverage.json",
        ignore_patterns: Optional[List[str]] = None,
        omit_patterns: Optional[List[str]] = None,
        # Extended options
        parallel_tests: bool = False,
        test_timeout: int = 300,
        custom_pytest_args: Optional[List[str]] = None
    ):
        super().__init__(source_dir, test_dir, output_file, ignore_patterns, omit_patterns)
        self.parallel_tests = parallel_tests
        self.test_timeout = test_timeout
        self.custom_pytest_args = custom_pytest_args or []

    def get_pytest_command(self) -> List[str]:
        """Build extended pytest command."""
        cmd = ["pytest"]

        if self.parallel_tests:
            cmd.extend(["-n", "auto"])  # pytest-xdist

        if self.test_timeout:
            cmd.extend(["--timeout", str(self.test_timeout)])

        cmd.extend(self.custom_pytest_args)

        return cmd

class ExtendedFLConfig(FLConfig):
    """Extended FL configuration with additional options."""

    def __init__(
        self,
        input_file: str = "coverage.json",
        output_file: str = "report.json",
        formulas: Optional[List[str]] = None,
        # Extended options
        min_confidence: float = 0.0,
        exclude_low_coverage: bool = False,
        custom_weights: Optional[Dict[str, float]] = None
    ):
        super().__init__(input_file, output_file, formulas)
        self.min_confidence = min_confidence
        self.exclude_low_coverage = exclude_low_coverage
        self.custom_weights = custom_weights or {}
```

### Batch Processing

```python
from pathlib import Path
from typing import List
import json

class BatchProcessor:
    """Process multiple projects with floss."""

    def __init__(self, base_config: TestConfig):
        self.base_config = base_config

    def process_projects(self, project_dirs: List[Path]) -> Dict[str, Dict]:
        """Process multiple projects and return aggregated results."""
        results = {}

        for project_dir in project_dirs:
            try:
                result = self.process_single_project(project_dir)
                results[str(project_dir)] = result
            except Exception as e:
                results[str(project_dir)] = {"error": str(e)}

        return results

    def process_single_project(self, project_dir: Path) -> Dict:
        """Process single project."""
        from floss.test import TestRunner
        from floss.fl import FLEngine, FLConfig

        # Create project-specific config
        config = TestConfig(
            source_dir=str(project_dir / self.base_config.source_dir),
            test_dir=str(project_dir / self.base_config.test_dir) if self.base_config.test_dir else None,
            output_file=str(project_dir / "coverage.json")
        )

        # Run tests
        runner = TestRunner(config)
        test_result = runner.run_tests()

        # Save coverage data
        with open(config.output_file, 'w') as f:
            json.dump(test_result.coverage_data, f)

        # Run fault localization if there are failed tests
        if test_result.failed_tests:
            fl_config = FLConfig(
                input_file=config.output_file,
                output_file=str(project_dir / "report.json"),
                formulas=["ochiai", "tarantula"]
            )

            engine = FLEngine(fl_config)
            engine.calculate_suspiciousness(fl_config.input_file, fl_config.output_file)

            # Load report
            with open(fl_config.output_file) as f:
                report = json.load(f)

            return {
                "status": "completed",
                "failed_tests": len(test_result.failed_tests),
                "max_suspiciousness": report.get("totals", {}).get("max_suspiciousness", 0)
            }
        else:
            return {
                "status": "no_failures",
                "failed_tests": 0
            }

# Usage
processor = BatchProcessor(TestConfig(source_dir="src", test_dir="tests"))
projects = [Path("project1"), Path("project2"), Path("project3")]
results = processor.process_projects(projects)

for project, result in results.items():
    print(f"{project}: {result}")
```

This API reference provides comprehensive documentation for integrating floss into your Python applications and extending its functionality for specific use cases.
