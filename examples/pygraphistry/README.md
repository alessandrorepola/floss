# PyGraphistry Example - Data Visualization Library

This example demonstrates PyFault's fault localization capabilities on PyGraphistry, a real-world data visualization library that provides graph analytics and visualization tools.

## Project Description

**Project**: PyGraphistry
**Category**: Data Visualization & Graph Analytics
**Language**: Python
**Domain**: Scientific Computing, Data Science

### Project Summary
PyGraphistry is a Python library that provides powerful graph visualization and analytics capabilities. It enables users to create interactive visualizations of network data, perform graph analytics, and integrate with various data sources.

### Why This Example
PyGraphistry represents a different class of software compared to web frameworks like FastAPI:
- **Scientific computing focus**: Complex mathematical operations and data processing
- **Visualization algorithms**: Graphics and rendering logic
- **Data pipeline architecture**: ETL and transformation operations
- **External integrations**: Database connectors and API clients

## Files Included

- `setup.sh`: Automated setup script that clones PyGraphistry and configures the environment
- `pyfault.conf`: Pre-configured PyFault settings optimized for PyGraphistry's structure
- `report.json`: Pre-generated fault localization results (when available)

## Setup Instructions

### Prerequisites
- Python 3.7+ (flexible version requirements compared to FastAPI examples)
- Git
- Unix-like environment (Linux/macOS/WSL)
- Internet connection

### Quick Setup
```bash
# Navigate to this directory
cd examples/pygraphistry

# Run setup script
./setup.sh

# The script will:
# 1. Create a Python virtual environment
# 2. Install PyFault
# 3. Clone PyGraphistry repository
# 4. Install dependencies
# 5. Copy configuration files
```

### Manual Setup
If the automated setup fails:

```bash
# Create virtual environment
python3 -m venv pygraphistry
source pygraphistry/bin/activate

# Install PyFault
pip install -e ../../

# Clone PyGraphistry
git clone https://github.com/graphistry/pygraphistry.git
cd pygraphistry

# Install dependencies
pip install -e .
pip install -r requirements-test.txt  # if available
```

## Running PyFault

After setup completes, run fault localization:

```bash
# Navigate to the PyGraphistry project directory
cd PyGraphistry

# Run complete fault localization pipeline
pyfault run --source-dir graphistry --test-dir tests

# Or run step by step:
pyfault test --source-dir graphistry --test-dir tests --output coverage.json
pyfault fl --input coverage.json --output report.json --formulas ochiai tarantula dstar2 jaccard
```

## Viewing Results

Launch the interactive dashboard:
```bash
pyfault ui --report report.json
```

The dashboard will show:
- **Treemap view**: Visual representation of PyGraphistry's module structure
- **Source code view**: Line-by-line analysis of visualization and analytics code
- **Coverage matrix**: Test coverage patterns for data processing pipelines
- **Formula comparison**: SBFL formula effectiveness on scientific computing code

## Expected Analysis Areas

PyFault will analyze various components:

### Core Modules
1. **Graph processing**: Node and edge manipulation algorithms
2. **Visualization engines**: Rendering and layout algorithms
3. **Data connectors**: Database and API integration modules
4. **Analytics functions**: Graph metrics and analysis algorithms

### Key Files to Examine
- `graphistry/plotter.py`: Core plotting and visualization logic
- `graphistry/pygraphistry.py`: Main API and orchestration
- `graphistry/layouts/`: Graph layout algorithms
- `graphistry/compute/`: Analytics and computation modules
- `graphistry/connectors/`: Data source integrations

## Analysis Tips

When analyzing PyGraphistry results:

1. **Focus on data pipelines** - trace how data flows through the system
2. **Examine algorithm implementations** - look for numerical computation bugs
3. **Check visualization logic** - rendering bugs often have specific patterns
4. **Analyze integration points** - external service connections are common failure points
5. **Look at error handling** - data processing systems need robust error handling

## Learning Objectives

This example demonstrates:
- How SBFL performs on scientific computing and data visualization code
- Differences in fault patterns between data processing vs web application bugs
- Impact of algorithm complexity on fault localization effectiveness
- Challenges of testing data visualization and graphics code

## Data Science Bug Patterns

Common bug types in data science libraries:
- **Data transformation errors**: Incorrect data processing or formatting
- **Algorithm implementation bugs**: Mathematical or logical errors in computations
- **Visualization rendering issues**: Graphics and display problems
- **Performance bottlenecks**: Inefficient algorithms causing slowdowns
- **Integration failures**: Problems connecting to data sources or external services

## Unique Challenges

PyGraphistry presents unique fault localization challenges:

### Data-Dependent Bugs
- Bugs that only appear with specific data patterns
- Edge cases in data processing pipelines
- Performance issues with large datasets

### Visualization Bugs
- Rendering problems that are hard to test automatically
- Layout algorithm issues
- Interactive feature failures

### Integration Complexity
- Multiple data source connectors
- External service dependencies
- Configuration and authentication issues

## Troubleshooting

### Setup Issues
- **Python version**: PyGraphistry supports multiple Python versions
- **Dependencies**: Graphics libraries might require system packages
- **Git issues**: Large repository might take time to clone

### Runtime Issues
- **Missing dependencies**: Graphics libraries might not be available
- **Data access**: Some tests might require external data sources
- **Performance**: Data processing tests might be slower than web framework tests

## Comparison with FastAPI Examples

PyGraphistry differs significantly:

| Aspect | FastAPI | PyGraphistry |
|--------|---------|---------------|
| **Domain** | Web APIs | Data Visualization |
| **Bug Types** | Validation, injection | Algorithms, rendering |
| **Test Patterns** | Request/response | Data processing |
| **Complexity** | Framework logic | Mathematical computation |
| **Dependencies** | Web stack | Scientific stack |

## Advanced Analysis

For deeper investigation:

1. **Algorithm testing**: Create test cases for specific graph algorithms
2. **Performance profiling**: Analyze performance-related code paths
3. **Data variation**: Test with different data sizes and structures
4. **Visualization validation**: Develop tests for visual output correctness

## Real-World Applications

PyGraphistry is used for:
- **Fraud detection**: Financial transaction analysis
- **Social network analysis**: Community detection and influence mapping
- **Cybersecurity**: Network traffic and threat analysis
- **Scientific research**: Complex network studies
- **Business analytics**: Customer behavior and operational analysis

## Next Steps

After exploring this example:
1. Compare fault patterns with web framework examples
2. Experiment with data science-specific SBFL formulas
3. Analyze how test coverage patterns differ in scientific computing
4. Create custom scenarios combining data processing and visualization bugs

## Contributing

To enhance this example:
1. Add specific failing test cases that represent common PyGraphistry issues
2. Create synthetic bugs in visualization or analytics modules
3. Develop test data sets that trigger specific bug patterns
4. Document domain-specific fault localization strategies
