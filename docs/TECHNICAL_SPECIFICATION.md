# PyFault Technical Specification

This document provides detailed technical specifications for the PyFault framework, including algorithms, data structures, and implementation details.

## 📋 Overview

PyFault implements Spectrum-Based Fault Localization (SBFL) techniques for Python codebases. The system follows a multi-phase pipeline architecture that transforms test execution data into actionable fault localization insights.

## 🔬 SBFL Algorithm Specification

### Core Algorithm

Spectrum-Based Fault Localization operates on the principle that program elements (lines, methods, classes) executed by failing tests are more likely to contain faults than those executed only by passing tests.

#### Input Requirements
- **Test Suite**: Collection of automated tests with deterministic outcomes
- **Source Code**: Python modules under analysis
- **Coverage Data**: Line-by-line execution traces for each test

#### Algorithm Steps

1. **Test Execution Phase**
   ```
   FOR each test t in test_suite:
       execute(t)
       record_coverage(t, source_code)
       record_outcome(t)  // PASS, FAIL, SKIP
   ```

2. **Coverage Matrix Construction**
   ```
   FOR each line l in source_code:
       FOR each test t in test_suite:
           coverage_matrix[l][t] = is_executed(l, t)
   ```

3. **Statistical Parameter Calculation**
   ```
   FOR each line l in source_code:
       n_cf = count(failed_tests_covering(l))
       n_nf = count(failed_tests_not_covering(l))
       n_cp = count(passed_tests_covering(l))
       n_np = count(passed_tests_not_covering(l))
   ```

4. **Suspiciousness Score Calculation**
   ```
   FOR each formula f in selected_formulas:
       FOR each line l in source_code:
           suspiciousness[f][l] = f.calculate(n_cf, n_nf, n_cp, n_np)
   ```

### Mathematical Foundations

#### SBFL Parameters

For each program line `l`, we define four fundamental parameters:

- **n_cf**: Number of failed tests that execute line `l`
- **n_nf**: Number of failed tests that do not execute line `l`
- **n_cp**: Number of passed tests that execute line `l`
- **n_np**: Number of passed tests that do not execute line `l`

**Invariants:**
- `n_cf + n_nf = total_failed_tests`
- `n_cp + n_np = total_passed_tests`
- `n_cf + n_cp = tests_covering_line`
- `n_nf + n_np = tests_not_covering_line`

#### Formula Implementations

##### Ochiai Formula
```
Formula: ochiai(n_cf, n_nf, n_cp, n_np) = n_cf / sqrt((n_cf + n_nf) * (n_cf + n_cp))

Properties:
- Range: [0, 1]
- Symmetric in n_nf and n_cp when n_cf > 0
- Returns 0 when n_cf = 0 (no failed tests cover the line)
- Approaches 1 when n_cf is high and n_cp is low

Time Complexity: O(1)
Space Complexity: O(1)
```

##### Tarantula Formula
```
Formula: tarantula(n_cf, n_nf, n_cp, n_np) = 
    (n_cf / (n_cf + n_nf)) / ((n_cf / (n_cf + n_nf)) + (n_cp / (n_cp + n_np)))

Properties:
- Range: [0, 1]
- Considers ratio of failed coverage vs. passed coverage
- Returns 0 when n_cf = 0
- Returns 1 when n_cp = 0 and n_cf > 0

Time Complexity: O(1)
Space Complexity: O(1)
```

##### Jaccard Formula
```
Formula: jaccard(n_cf, n_nf, n_cp, n_np) = n_cf / (n_cf + n_nf + n_cp)

Properties:
- Range: [0, 1]
- Intersection over union of failed tests and tests covering the line
- Ignores passed tests not covering the line (n_np)
- More conservative than Ochiai and Tarantula

Time Complexity: O(1)
Space Complexity: O(1)
```

##### D* Formula
```
Formula: dstar(n_cf, n_nf, n_cp, n_np, star) = (n_cf)^star / (n_cp + n_nf)

Properties:
- Range: [0, ∞)
- Parameterizable exponent (typically star = 2 or 3)
- Higher values indicate higher suspiciousness
- Returns 0 when n_cf = 0
- Unbounded upper range allows fine discrimination

Time Complexity: O(1)
Space Complexity: O(1)
```

## 🏗️ System Architecture Specification

### Component Hierarchy

```
PyFault System
├── CLI Layer (pyfault.cli)
│   ├── Command Parser (Click framework)
│   ├── Configuration Manager
│   └── Output Formatter (Rich library)
├── Application Layer
│   ├── Test Runner (pyfault.test)
│   │   ├── pytest Integration
│   │   ├── Coverage Collection
│   │   └── Result Processing
│   └── FL Engine (pyfault.fl)
│       ├── Coverage Analysis
│       ├── Formula Application
│       └── Report Generation
├── Formula Layer (pyfault.formulas)
│   ├── Abstract Base Class
│   ├── Concrete Implementations
│   └── Utility Functions
└── UI Layer (pyfault.ui)
    ├── Streamlit Framework
    ├── Plotly Visualizations
    └── Interactive Components
```

### Data Flow Specification

#### Phase 1: Test Execution and Coverage Collection

**Input:** Source code, test suite, configuration
**Output:** Coverage matrix with test outcomes

```python
# Data Structure: Coverage Context
{
    "line_id": str,              # Format: "file_path:line_number"
    "test_contexts": List[str],  # Tests that executed this line
    "execution_count": int       # Number of times line was executed
}

# Data Structure: Test Outcome
{
    "test_id": str,              # Unique test identifier
    "outcome": str,              # "PASSED", "FAILED", "SKIPPED"
    "execution_time": float,     # Test execution time in seconds
    "error_message": Optional[str]  # Error message if failed
}
```

#### Phase 2: Fault Localization Calculation

**Input:** Coverage matrix, test outcomes, formula selection
**Output:** Suspiciousness scores per line per formula

```python
# Data Structure: Suspiciousness Score
{
    "line_id": str,                    # Format: "file_path:line_number"
    "formula_scores": Dict[str, float] # Formula name to score mapping
}

# Data Structure: FL Report
{
    "meta": {
        "timestamp": str,
        "pyfault_version": str,
        "formulas_used": List[str]
    },
    "totals": {
        "test_statistics": {...},
        "analysis_statistics": {...},
        "sbfl_formulas": List[str]
    },
    "files": {
        "file_path": {
            "suspiciousness": {
                "formula_name": {
                    "line_number": float
                }
            },
            "coverage_data": {...}
        }
    }
}
```

### Performance Specifications

#### Computational Complexity

**Test Execution Phase:**
- Time Complexity: O(T × L) where T = number of tests, L = lines of code
- Space Complexity: O(T × L) for coverage matrix storage

**FL Calculation Phase:**
- Time Complexity: O(L × F) where L = lines with coverage, F = number of formulas
- Space Complexity: O(L × F) for suspiciousness scores

**Total System Complexity:**
- Time: O(T × L + L × F) ≈ O(T × L) for typical F << T
- Space: O(T × L + L × F) ≈ O(T × L) for typical F << T

#### Scalability Limits

| Project Size | Lines of Code | Tests | Memory Usage | Execution Time |
|--------------|---------------|-------|--------------|----------------|
| Small        | < 1,000       | < 100 | < 50 MB      | < 10 seconds   |
| Medium       | 1,000-10,000  | 100-1,000 | 50-500 MB | 10-60 seconds  |
| Large        | 10,000-100,000| 1,000-10,000 | 500MB-5GB | 1-10 minutes   |
| Enterprise   | > 100,000     | > 10,000 | > 5 GB       | > 10 minutes   |

## 🔧 Implementation Details

### Test Runner Implementation

#### pytest Integration

```python
def _build_pytest_command(self, xml_path: str, test_filter: Optional[str] = None) -> List[str]:
    """Build pytest command with coverage options."""
    cmd = ["pytest"]
    
    # Coverage options
    cmd.extend([
        f"--cov={self.config.source_dir}",
        "--cov-context=test",                    # Enable context tracking
        f"--cov-report=json:{self.config.output_file}",
        "--cov-branch",                          # Include branch coverage
        f"--junitxml={xml_path}"                # XML output for test results
    ])
    
    return cmd
```

#### Coverage Data Processing

```python
def _remove_redundant_contexts(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove function and class contexts, keeping only test contexts."""
    for file_path, file_data in coverage_data.get("files", {}).items():
        if "contexts" in file_data:
            # Filter contexts to include only test functions
            test_contexts = {
                context: lines for context, lines in file_data["contexts"].items()
                if context.startswith("test_") or "::test_" in context
            }
            file_data["contexts"] = test_contexts
    
    return coverage_data
```

### FL Engine Implementation

#### Formula Registry

```python
AVAILABLE_FORMULAS = {
    "ochiai": OchiaiFormula(),
    "tarantula": TarantulaFormula(),
    "jaccard": JaccardFormula(),
    "dstar2": DStarFormula(star=2),
    "dstar3": DStarFormula(star=3),
}
```

#### Score Calculation Algorithm

```python
def calculate_suspiciousness(self, input_file: str, output_file: str) -> None:
    """Calculate suspiciousness scores for all lines and formulas."""
    coverage_data = CoverageData.from_json(self._load_coverage_json(input_file))
    
    suspiciousness_scores = {}
    
    for line_key in coverage_data.line_coverage:
        # Extract SBFL parameters
        n_cf, n_nf, n_cp, n_np = coverage_data.get_sbfl_params(line_key)
        
        # Calculate score for each formula
        line_scores = {}
        for formula_name, formula in self.formulas.items():
            score = formula.calculate(n_cf, n_nf, n_cp, n_np)
            line_scores[formula_name] = score
        
        suspiciousness_scores[line_key] = line_scores
    
    self._generate_report(suspiciousness_scores, coverage_data, output_file)
```

### Formula Base Class

```python
class SBFLFormula:
    """Abstract base class for SBFL formulas."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """Calculate suspiciousness score."""
        pass
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
```

## 📊 Data Structure Specifications

### Coverage Data Structure

```python
@dataclass
class CoverageData:
    """Structured representation of coverage information."""
    
    # Core data
    line_coverage: Dict[str, List[str]]  # line_id -> [test_ids]
    test_outcomes: Dict[str, bool]       # test_id -> passed
    file_metadata: Dict[str, Dict]       # file_path -> metadata
    
    # Derived statistics
    total_tests: int
    failed_tests: List[str]
    passed_tests: List[str]
    
    def get_sbfl_params(self, line_key: str) -> Tuple[int, int, int, int]:
        """Extract SBFL parameters for a given line."""
        covering_tests = set(self.line_coverage.get(line_key, []))
        
        n_cf = len([t for t in covering_tests if not self.test_outcomes.get(t, True)])
        n_cp = len([t for t in covering_tests if self.test_outcomes.get(t, True)])
        n_nf = len(self.failed_tests) - n_cf
        n_np = len(self.passed_tests) - n_cp
        
        return n_cf, n_nf, n_cp, n_np
```

### Configuration Schema

```python
# pyfault.conf schema
[test]
source_dir = string          # Required: source code directory
test_dir = string?           # Optional: test directory (auto-detected if not set)
output_file = string         # Coverage output file (default: coverage.json)
ignore = string_list?        # Patterns to ignore in test discovery
omit = string_list?          # Patterns to omit from coverage

[fl]
input_file = string          # Coverage input file (default: coverage.json)
output_file = string         # FL report output file (default: report.json)
formulas = string_list       # SBFL formulas to apply (default: ochiai,tarantula,jaccard,dstar2)
```

## 🔒 Quality Assurance Specifications

### Input Validation

#### Configuration Validation
```python
def validate_config(config: TestConfig) -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []
    
    if not os.path.exists(config.source_dir):
        errors.append(f"Source directory does not exist: {config.source_dir}")
    
    if config.test_dir and not os.path.exists(config.test_dir):
        errors.append(f"Test directory does not exist: {config.test_dir}")
    
    return errors
```

#### Data Validation
```python
def validate_coverage_data(data: Dict[str, Any]) -> bool:
    """Validate coverage data structure."""
    required_keys = ["meta", "files", "totals"]
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key in coverage data: {key}")
    
    # Validate file structure
    for file_path, file_data in data["files"].items():
        if "contexts" not in file_data:
            raise ValueError(f"Missing contexts for file: {file_path}")
    
    return True
```

### Error Handling Specifications

#### Exception Hierarchy
```python
class PyFaultError(Exception):
    """Base exception for PyFault."""
    pass

class ConfigurationError(PyFaultError):
    """Configuration-related errors."""
    pass

class TestExecutionError(PyFaultError):
    """Test execution failures."""
    pass

class DataProcessingError(PyFaultError):
    """Data processing errors."""
    pass

class FormulaError(PyFaultError):
    """Formula calculation errors."""
    pass
```

#### Error Recovery Strategies

1. **Configuration Errors**: Provide default values where possible
2. **Test Execution Errors**: Retry with simplified parameters
3. **Data Processing Errors**: Skip corrupted entries, continue processing
4. **Formula Errors**: Return 0.0 score, log warning

### Testing Specifications

#### Test Categories

1. **Unit Tests**: Individual component testing
   - Formula calculations with edge cases
   - Configuration loading and validation
   - Data structure operations

2. **Integration Tests**: Component interaction testing
   - Test runner with coverage collection
   - FL engine with formula application
   - CLI command execution

3. **End-to-End Tests**: Complete pipeline testing
   - Full workflow from source code to report
   - Dashboard visualization with real data
   - Error handling in complete scenarios

4. **Performance Tests**: Scalability and efficiency testing
   - Large codebase processing
   - Memory usage monitoring
   - Execution time benchmarking

#### Test Data Requirements

```python
# Minimal test project structure
test_project/
├── src/
│   └── module.py      # At least 10 lines with mixed coverage
├── tests/
│   └── test_module.py # At least 5 tests (3 pass, 2 fail)
└── pyfault.conf       # Basic configuration
```

## 🔄 Extension Specifications

### Adding New SBFL Formulas

#### Interface Contract
```python
class NewFormula(SBFLFormula):
    def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
        """
        Calculate suspiciousness score.
        
        Args:
            n_cf: Failed tests covering line (>= 0)
            n_nf: Failed tests not covering line (>= 0)
            n_cp: Passed tests covering line (>= 0)
            n_np: Passed tests not covering line (>= 0)
        
        Returns:
            Suspiciousness score (typically 0.0 to 1.0, may be unbounded)
        
        Invariants:
            - Must handle n_cf = 0 case (return 0.0 is common)
            - Must be deterministic for same inputs
            - Should be numerically stable
        """
        pass
```

#### Registration Process
```python
# 1. Add to formula registry
FLEngine.AVAILABLE_FORMULAS["new_formula"] = NewFormula()

# 2. Add tests
class TestNewFormula:
    def test_basic_calculation(self):
        formula = NewFormula()
        assert formula.calculate(5, 3, 2, 10) == expected_value
    
    def test_edge_cases(self):
        formula = NewFormula()
        assert formula.calculate(0, 5, 3, 2) == 0.0  # No failed covering
        # Test other edge cases...

# 3. Update documentation
```

### Dashboard Extension Points

#### Custom Visualization Components
```python
def show_custom_visualization(data: Dict[str, Any], formula: str):
    """Add custom visualization to dashboard."""
    st.subheader("Custom Analysis")
    
    # Extract relevant data
    files_data = data.get("files", {})
    
    # Create custom Plotly figure
    fig = create_custom_plot(files_data, formula)
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
```

#### Tab Registration
```python
# Add to main dashboard function
with st.tabs([..., "Custom Tab"]):
    show_custom_visualization(data, selected_formula)
```

## 📈 Performance Optimization Guidelines

### Memory Optimization

1. **Lazy Loading**: Load coverage data on demand
2. **Data Compression**: Use efficient data structures
3. **Garbage Collection**: Explicit cleanup of large objects
4. **Streaming**: Process large files in chunks

### Computational Optimization

1. **Vectorization**: Use NumPy for batch calculations where possible
2. **Caching**: Cache expensive calculations
3. **Parallel Processing**: Use multiprocessing for independent calculations
4. **Algorithm Selection**: Choose appropriate algorithms for data size

### I/O Optimization

1. **Buffered I/O**: Use appropriate buffer sizes for file operations
2. **JSON Streaming**: Use streaming JSON parser for large files
3. **Compression**: Compress intermediate files when possible
4. **Batch Operations**: Minimize file system operations

This technical specification provides the foundation for understanding, implementing, and extending the PyFault system. It serves as a reference for developers, researchers, and contributors working with the codebase.
