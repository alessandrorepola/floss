# FastAPI Bug 2 - OpenAPI Schema Generation Issue

This example demonstrates PyFault's fault localization capabilities on FastAPI Bug #2, which involves an issue with OpenAPI schema generation for complex response models.

## Bug Description

**Bug ID**: FastAPI Bug #2 from BugsInPy dataset  
**Category**: OpenAPI Schema Generation  
**Severity**: Medium  
**Language**: Python 3.8.3  

### Problem Summary
The bug occurs when FastAPI attempts to generate OpenAPI schemas for response models that contain certain types of nested structures. The schema generation fails with incorrect type inference, causing API documentation to be malformed.

### Expected vs Actual Behavior
- **Expected**: Proper OpenAPI schema generation for nested response models
- **Actual**: Schema generation fails or produces incorrect schemas
- **Impact**: API documentation becomes unusable, affecting developer experience

## Files Included

- `setup.sh`: Automated setup script that downloads FastAPI v0.2 and configures the test environment
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
cd examples/fastapi/bug2

# Run setup script (this will take a few minutes)
./setup.sh

# The script will:
# 1. Create a Python 3.8.3 virtual environment
# 2. Install PyFault
# 3. Clone BugsInPy framework
# 4. Download FastAPI v0.2 with the bug
# 5. Install dependencies
# 6. Copy configuration files
```

### Manual Setup
If the automated setup fails, you can set up manually:

```bash
# Create virtual environment with Python 3.8.3
python3.8 -m venv fastapi-bug2
source fastapi-bug2/bin/activate

# Install PyFault
pip install -e ../../../

# Clone BugsInPy
git clone https://github.com/soarsmu/BugsInPy.git
export PATH="$PATH:$(pwd)/BugsInPy/framework/bin"

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 2 -w "./"

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
pyfault fl --input coverage.json --output report.json --formulas ochiai tarantula dstar2
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
1. **OpenAPI schema generation functions** (highest suspiciousness)
2. **Response model validation logic** (medium suspiciousness)  
3. **Type inference utilities** (medium suspiciousness)

Key files to examine:
- `fastapi/openapi/utils.py`: Schema generation logic
- `fastapi/utils.py`: Utility functions for type handling
- `fastapi/routing.py`: Route and response handling

## Analysis Tips

When analyzing the results:

1. **Focus on high-suspiciousness lines** in schema generation code
2. **Look for test patterns** - which tests pass vs fail
3. **Compare different SBFL formulas** - Ochiai and Tarantula often work well for this type of bug
4. **Examine test coverage** - uncovered lines might indicate missing test cases

## Learning Objectives

This example demonstrates:
- How PyFault handles complex Python frameworks
- Effectiveness of SBFL on API schema generation bugs
- Impact of test coverage on fault localization accuracy
- Comparison of different SBFL formulas on real-world bugs

## Troubleshooting

### Setup Issues
- **Python version**: Ensure exactly Python 3.8.3 is used
- **BugsInPy errors**: Check internet connection and git configuration
- **Permission errors**: Run `chmod +x setup.sh`

### Runtime Issues
- **Import errors**: Ensure virtual environment is activated
- **Test failures**: Some tests are expected to fail (this is the bug!)
- **Memory issues**: Close other applications if running low on memory

## Next Steps

After exploring this example:
1. Try the other FastAPI bug examples (bug3, bug6, bug11)
2. Experiment with different SBFL formulas
3. Add custom test cases to see how they affect results
4. Compare results with manual debugging approaches
