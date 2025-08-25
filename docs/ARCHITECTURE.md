# PyFault Technical Architecture

The high‑level pipeline consists of three phases: test execution and coverage collection, fault localization, and visualization. The diagram below summarizes the actual flow and artifacts.

![Architecture Diagram](imgs/pyfault_arch.png)

## System Overview

PyFault is a modular framework designed for automated fault localization using Spectrum-Based Fault Localization (SBFL) techniques. The system follows a layered architecture pattern with clear separation of concerns and well-defined interfaces between components.

Pipeline at a glance:
- Phase 1: pytest (with pytest-cov) runs tests and collects contexts; Test Runner merges coverage.py JSON and pytest test outcomes into a single coverage.json that conceptually represents the coverage matrix (lines × tests).
- Phase 2: FL Engine reads coverage.json, computes suspiciousness using configured formulas, and writes a consolidated report.json augmenting the previous data.
- Phase 3: The Streamlit dashboard visualizes report.json.

## Architectural Principles

### 1. **Modularity**
- Each component has a single responsibility
- Clean interfaces between layers
- Pluggable formula implementations
- Independent test execution and fault localization phases

### 2. **Extensibility**
- Abstract base classes for easy extension
- Plugin-like formula system
- Configurable pipeline stages
- Support for custom visualization components

### 3. **Usability**
- Command-line interface for automation
- Interactive web dashboard for exploration
- Configuration file support
- Rich error reporting and logging

### 4. **Performance**
- Efficient coverage data processing
- Optimized suspiciousness calculations
- Caching mechanisms in dashboard
- Minimal memory footprint for large projects

## Component Architecture

### Command-Line Interface (CLI) Layer

The CLI layer provides the primary interface for user interaction with PyFault. It consists of four main commands:

```
pyfault/
├── cli/
│   ├── main.py          # Entry point and command definitions
│   └── __init__.py      # Package exports
```

#### Command Structure:

1. **`pyfault test`** - Test execution with coverage collection
2. **`pyfault fl`** - Fault localization calculation
3. **`pyfault run`** - Complete pipeline execution
4. **`pyfault ui`** - Dashboard launch

Each command follows a consistent pattern:
- Configuration loading (file + CLI overrides)
- Input validation
- Core component invocation
- Result reporting
- Error handling

### Core Components Layer

#### Test Runner Component

**Location**: `pyfault/core/test/`

**Responsibilities**:
- Integration with pytest for test execution (via pytest-cov)
- Coverage data collection using coverage.py with test contexts
- Test outcome parsing from temporary JUnit XML
- Merge coverage contexts and test outcomes into a single coverage.json (coverage matrix)
- Metadata generation and redundant context cleanup

**Key Classes**:
- `TestRunner`: Main execution coordinator
- `TestConfig`: Configuration management
- `TestResult`: Result data structure

**Architecture**:
```python
TestRunner
├── Configuration Loading
├── pytest Command Building
├── Coverage Context Collection
├── XML Result Parsing
├── Coverage Data Enhancement
└── Result Aggregation
```

**Data Flow**:
1. Load configuration from file and CLI arguments
2. Generate pytest command with coverage options
3. Execute tests in subprocess
4. Parse temporary JUnit XML for test outcomes
5. Load coverage.py JSON output
6. Remove redundant function/class contexts; integrate test outcomes into file-level contexts
7. Add PyFault-specific metadata and summary
8. Produce a single coverage.json (final artifact of Phase 1) and return structured TestResult

#### Fault Localization Engine

**Location**: `pyfault/core/fl/`

**Responsibilities**:
- SBFL formula application
- Suspiciousness score calculation
- Report generation and enhancement
- Metadata aggregation

**Key Classes**:
- `FLEngine`: Core calculation engine
- `FLConfig`: Configuration management
- `CoverageData`: Data structure abstraction

**Architecture**:
```python
FLEngine
├── Formula Registry
├── Coverage Data Loading
├── SBFL Parameter Calculation
├── Suspiciousness Scoring
├── Report Enhancement
└── Metadata Generation
```

**Calculation Process**:
1. Load coverage.json from Phase 1
2. Extract SBFL parameters (n_cf, n_nf, n_cp, n_np) for each line from merged contexts and outcomes
3. Apply configured formulas to compute suspiciousness
4. Add suspiciousness to per-file sections; add FL metadata and totals
5. Write consolidated report.json (final artifact of Phase 2)

#### Interactive Dashboard

**Location**: `pyfault/ui/`

**Responsibilities**:
- Web-based result visualization
- Interactive data exploration
- Multiple chart types and views
- Export and sharing capabilities

**Key Features**:
- Streamlit-based web interface
- Plotly for interactive charts
- File selection and loading
- Real-time filtering and analysis

**Visualization Types**:
1. **Treemap**: Hierarchical project view with suspiciousness coloring
2. **Sunburst**: Circular hierarchical visualization
3. **Coverage Matrix**: Test-to-code coverage visualization
4. **Source Code Viewer**: Syntax-highlighted code with overlays
5. **Statistics Dashboard**: Analytical views and comparisons

### SBFL Formulas Layer

**Location**: `pyfault/core/formulas/`

**Architecture**:
```python
SBFLFormula (Abstract Base Class)
├── OchiaiFormula
├── TarantulaFormula
├── JaccardFormula
├── DStarFormula
├── Kulczynski2Formula
├── Naish1Formula
├── RussellRaoFormula
├── SorensenDiceFormula
└── SBIFormula
```

**Design Pattern**: Strategy Pattern
- Each formula implements the same `calculate()` interface
- Formulas are registered in the FL engine's formula registry
- Easy addition of new formulas without modifying existing code

**Formula Interface**:
```python
def calculate(self, n_cf: int, n_nf: int, n_cp: int, n_np: int) -> float:
    """Calculate suspiciousness score given SBFL parameters."""
    pass
```

## Data Flow Architecture

### 1. Test Execution Phase

```
Source Code (.py files)
    ↓
pytest + coverage.py (contexts)
    ↓
Temporary: JUnit XML (pytest) + coverage.py JSON
    ↓
Merged into a single coverage.json (coverage matrix: lines ⇄ tests)
```

### 2. Fault Localization Phase

```
coverage.json (from Phase 1)
    ↓
SBFL Parameter Extraction (n_cf, n_nf, n_cp, n_np)
    ↓
Formula Application (Ochiai, Tarantula, etc.)
    ↓
Suspiciousness Score Calculation and integration
  ↓
report.json (coverage + suspiciousness + metadata)
```

### 3. Visualization Phase

```
report.json
    ↓
Streamlit Dashboard
    ↓
Interactive Visualizations (Plotly)
    ↓
User Exploration and Analysis
```

Note on implementation details (from code):
- The Test Runner builds pytest with: --cov, --cov-context=test, --cov-branch, and --cov-report=json:<output> (see `pyfault/core/test/runner.py::_build_pytest_command`).
- JUnit XML is parsed and then removed; coverage.py JSON is read and then merged; redundant function/class contexts are removed to reduce size (see `pyfault/core/test/runner.py::_remove_redundant_contexts`).
- Test outcomes are merged under the tests section, and meta/totals are enriched (see `pyfault/core/test/runner.py`).
- The FL Engine reads coverage.json, computes scores for each line using formulas, writes them into files[*].suspiciousness, and outputs report.json with fl_metadata and totals (see `pyfault/core/fl/engine.py`).

## Configuration System

PyFault uses a hierarchical configuration system with the following precedence (highest to lowest):

1. **Command-line arguments**
2. **Configuration file values**
3. **Default values**

### Configuration File Format

```ini
[test]
source_dir = src
test_dir = tests
output_file = coverage.json
ignore = */__init__.py, */migrations/*
omit = */__init__.py, */test_*

[fl]
input_file = coverage.json
output_file = report.json
formulas = ochiai, tarantula, jaccard, dstar2
```

### Configuration Classes

- `TestConfig`: Test execution parameters
- `FLConfig`: Fault localization parameters

Both support:
- File-based loading (`from_file()` method)
- Validation and default value handling
- Integration with CLI argument parsing

## Data Structures

### Coverage Data Format

PyFault uses an enhanced version of coverage.py's JSON format:

```json
{
  "meta": {
    "format": 3,
    "version": "7.9.2",
    "timestamp": "2025-01-01T12:00:00Z",
    "branch_coverage": true,
    "show_contexts": true,
    "phase": "test_execution",
    "tool": "PyFault",
    "tool_version": "0.1.0"
  },
  "files": {
    "src/module.py": {
      "executed_lines": [1, 2, 5, 7],
      "contexts": {
        "1": ["test_file::test_name|run"],
        "2": ["test_file::test_name|run", "test_file::test_other|run"]
      },
      "suspiciousness": {
        "1": {
          "ochiai": 0.85,
          "tarantula": 0.72,
          "jaccard": 0.65
        }
      }
    }
  },
  "test_outcomes": {
    "test_file::test_name": true,
    "test_file::test_other": false
  },
  "totals": {
    "total_tests": 10,
    "passed_tests": 8,
    "failed_tests": 2,
    "lines_analyzed": 150,
    "max_suspiciousness": 0.95
  }
}
```

### Report Enhancement

The FL engine enhances coverage data with:
- Suspiciousness scores for each line
- Formula-specific metadata
- Statistical summaries
- Phase tracking information

## Error Handling and Logging

### Error Handling Strategy

1. **Input Validation**: Early validation with clear error messages
2. **Graceful Degradation**: Continue processing when possible
3. **Rich Error Reporting**: Colored terminal output with context
4. **Debug Information**: Verbose mode for troubleshooting

### Logging System

- **Rich Handler**: Colored console output with tracebacks
- **Configurable Levels**: INFO (default) and DEBUG (verbose mode)
- **Structured Messages**: Consistent formatting across components

## Performance Considerations

### Test Execution
- **Subprocess Isolation**: Tests run in separate process
- **Parallel Test Support**: Leverages pytest's parallelization
- **Selective Coverage**: Configurable file patterns for inclusion/exclusion

### Fault Localization
- **Efficient Data Structures**: NumPy arrays for calculations
- **Formula Optimization**: Cached parameter calculations
- **Memory Management**: Streaming JSON processing for large files

### Dashboard
- **Caching**: Pre-calculated statistics and aggregations
- **Lazy Loading**: On-demand data processing
- **Responsive Design**: Efficient rendering for large datasets

## Integration Points

### External Tool Integration

1. **pytest**: Test execution and discovery
2. **coverage.py**: Coverage measurement and context collection
3. **Streamlit**: Web dashboard framework
4. **Plotly**: Interactive visualization library

### API Integration

PyFault provides programmatic APIs for:
- Custom test runners
- Formula implementations
- Dashboard extensions
- Configuration management

### CI/CD Integration

Support for continuous integration through:
- Command-line interface
- JSON report generation
- Exit code handling
- Configurable output formats

## Security Considerations

### Input Validation
- File path sanitization
- JSON schema validation
- Configuration parameter bounds checking

### Execution Safety
- Subprocess sandboxing for test execution
- Temporary file cleanup
- Resource limitation support

### Data Privacy
- Local processing (no external data transmission)
- Configurable output redaction
- Secure temporary file handling

## Scalability and Limits

### Current Limitations
- Single-machine processing
- Memory-based data structures
- JSON file format constraints

### Scalability Considerations
- File size limits (~100MB JSON reports)
- Memory usage scales with project size
- Dashboard performance with >10k lines

### Future Scalability Options
- Database backend support
- Distributed processing capabilities
- Streaming data processing
- Cloud deployment options

## Extension Points

### Adding New SBFL Formulas

1. Implement `SBFLFormula` interface
2. Add to formula registry in `FLEngine`
3. Include in package exports
4. Add comprehensive tests

### Custom Visualizations

1. Extend dashboard with new Streamlit components
2. Implement custom Plotly chart types
3. Add interactive filtering options
4. Support export formats

### Integration Extensions

1. Custom test runners (beyond pytest)
2. Alternative coverage tools
3. Different report formats
4. External tool integrations

This architecture supports PyFault's goals of providing a comprehensive, extensible, and user-friendly fault localization framework for Python projects.
