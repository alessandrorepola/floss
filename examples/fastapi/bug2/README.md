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

- `README.md`: This file with bug-specific documentation
- `report.json`: Pre-generated fault localization results showing the most suspicious lines

## Setup Instructions

### Prerequisites
- Python 3.8.3 (exact version required)
- Git
- Unix-like environment (Linux/macOS/WSL)

### Quick Setup
```bash
# Navigate to the fastapi examples directory
cd examples/fastapi

# Run the centralized setup script for bug 2
./setup.sh 2
```

### Manual Setup (Alternative)
If the automated setup fails:

```bash
# From the fastapi directory  
cd examples/fastapi

# Create virtual environment with Python 3.8.3
python3.8 -m venv fastapi-bug2
source fastapi-bug2/bin/activate

# Install PyFault
pip install -e ../../

# Clone BugsInPy
git clone https://github.com/soarsmu/BugsInPy.git
export PATH="$PATH:$(pwd)/BugsInPy/framework/bin"

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 2 -w "./"

# Install dependencies
cd fastapi && pip install -r bugsinpy_requirements.txt && pip install -e .
```

## Running PyFault

After setup completes:

```bash
# Activate environment (if not already active)
source fastapi-bug2/bin/activate

# Navigate to the FastAPI project directory
cd fastapi

# Run fault localization
pyfault run
```

## Expected Results

The fault localization should identify suspicious code in:

| Priority | Component | Expected Files |
|----------|-----------|----------------|
| **High** | OpenAPI schema generation | `fastapi/openapi/utils.py`, `fastapi/routing.py` |
| **Medium** | Model introspection | `fastapi/utils.py`, `pydantic` integration |
| **Low** | Type annotation processing | Model definition files |

## Bug Analysis

**Nature of the Bug**: OpenAPI schema generation fails for complex nested response models

**What to Look For**:
- Schema generation failures with nested structures
- Incorrect type inference in OpenAPI schemas
- Malformed API documentation

**Key Concepts**:
- **OpenAPI Schema**: JSON schema describing API endpoints and data models
- **Type Introspection**: Analysis of Python type annotations for schema generation
- **Nested Models**: Response models containing other complex models
## Viewing Results

Launch the interactive dashboard:
```bash
pyfault ui --report report.json
```

The dashboard provides:
- **Treemap view**: Visual file suspiciousness
- **Source code view**: Line-by-line analysis  
- **Coverage matrix**: Test execution patterns
- **Formula comparison**: Multiple SBFL formula results

## Analysis Tips

When analyzing the results:
1. **Focus on schema generation code** - look for high suspiciousness in OpenAPI utilities
2. **Examine type introspection logic** - understand how types are analyzed
3. **Compare different SBFL formulas** - Ochiai and Tarantula often work well for this bug type
4. **Review test coverage patterns** - identify which nested models cause failures
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
