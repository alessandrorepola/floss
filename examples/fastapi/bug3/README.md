# FastAPI Bug 3 - Request Validation Problem

This example demonstrates PyFault's fault localization capabilities on FastAPI Bug #3, which involves incorrect request validation behavior for specific parameter types.

## Bug Description

**Bug ID**: FastAPI Bug #3 from BugsInPy dataset  
**Category**: Request Validation  
**Severity**: High  
**Language**: Python 3.8.3  

### Problem Summary
The bug occurs during request parameter validation when FastAPI incorrectly handles certain parameter types or validation constraints. This leads to either false validation errors for valid requests or acceptance of invalid requests that should be rejected.

### Expected vs Actual Behavior
- **Expected**: Correct validation of request parameters according to defined schemas
- **Actual**: Validation logic incorrectly accepts/rejects certain parameter combinations
- **Impact**: API security and data integrity issues, poor user experience

## Files Included

- `setup.sh`: Automated setup script that downloads FastAPI v0.3 and configures the test environment
- `pyfault.conf`: Pre-configured PyFault settings optimized for FastAPI's structure
- `report.json`: Pre-generated fault localization results showing the most suspicious lines

## Setup Instructions

### Prerequisites
- Python 3.8.3 (exact version required)
- Git
- Unix-like environment (Linux/macOS/WSL)

### Quick Setup
```bash
# Navigate to this directory
cd examples/fastapi/bug3

# Run setup script (this will take a few minutes)
./setup.sh

# The script will:
# 1. Create a Python 3.8.3 virtual environment
# 2. Install PyFault
# 3. Clone BugsInPy framework
# 4. Download FastAPI v0.3 with the bug
# 5. Install dependencies
# 6. Copy configuration files
```

### Manual Setup
If the automated setup fails, you can set up manually:

```bash
# Create virtual environment with Python 3.8.3
python3.8 -m venv fastapi-bug3
source fastapi-bug3/bin/activate

# Install PyFault
pip install -e ../../../

# Clone BugsInPy
git clone https://github.com/soarsmu/BugsInPy.git
export PATH="$PATH:$(pwd)/BugsInPy/framework/bin"

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 3 -w "./"

# Install dependencies
cd fastapi
pip install -r bugsinpy_requirements.txt
pip install -e .
```

## Running PyFault

After setup completes, run fault localization:

```bash
# Navigate to the FastAPI project directory
cd fastapi

# Run complete fault localization pipeline
pyfault run

# Or run step by step:
pyfault test --source-dir fastapi --test-dir tests
pyfault fl --input coverage.json --output report.json --formulas ochiai tarantula dstar2 jaccard
```

## Viewing Results

Launch the interactive dashboard:
```bash
pyfault ui --report report.json
```

The dashboard will show:
- **Treemap view**: Visual representation of file suspiciousness
- **Source code view**: Line-by-line suspiciousness scores
- **Coverage matrix**: Test execution patterns
- **Formula comparison**: Different SBFL formula results

## Expected Results

The fault localization should identify suspicious code in:
1. **Request validation functions** (highest suspiciousness)
2. **Parameter parsing logic** (high suspiciousness)  
3. **Type conversion utilities** (medium suspiciousness)
4. **Schema validation handlers** (medium suspiciousness)

Key files to examine:
- `fastapi/params.py`: Parameter handling and validation
- `fastapi/dependencies/utils.py`: Dependency injection and validation
- `fastapi/utils.py`: Type conversion and validation utilities
- `fastapi/routing.py`: Request routing and parameter extraction

## Analysis Tips

When analyzing the results:

1. **Focus on validation logic** - look for conditions that handle parameter validation
2. **Examine test failures** - understand which validation scenarios are failing
3. **Check parameter types** - different data types might be handled differently
4. **Look for edge cases** - validation bugs often occur at boundary conditions

## Learning Objectives

This example demonstrates:
- How SBFL performs on input validation bugs
- Importance of comprehensive test coverage for validation logic
- Impact of parameter type complexity on fault localization
- Effectiveness of different SBFL formulas on validation-related bugs

## Common Validation Bug Patterns

This bug type typically involves:
- **Type coercion errors**: Incorrect conversion between data types
- **Constraint validation**: Failing to properly validate min/max values, string lengths, etc.
- **Optional parameter handling**: Issues with required vs optional parameters
- **Nested validation**: Problems with validating complex nested data structures

## Troubleshooting

### Setup Issues
- **Python version**: Ensure exactly Python 3.8.3 is used
- **BugsInPy errors**: Check internet connection and git configuration
- **Permission errors**: Run `chmod +x setup.sh`

### Runtime Issues
- **Import errors**: Ensure virtual environment is activated
- **Test failures**: Some tests are expected to fail (this is the bug!)
- **Validation errors**: During testing, some validation might behave unexpectedly

## Deep Dive Analysis

For advanced analysis:

1. **Manual debugging**: Set breakpoints in validation functions
2. **Test case analysis**: Create additional test cases to narrow down the bug
3. **Parameter combinations**: Test different parameter type combinations
4. **Regression testing**: Verify the fix doesn't break other functionality

## Next Steps

After exploring this example:
1. Compare with other FastAPI bugs to see different bug patterns
2. Try modifying test cases to see how it affects suspiciousness scores
3. Experiment with adding new SBFL formulas
4. Analyze the relationship between test coverage and fault localization accuracy
